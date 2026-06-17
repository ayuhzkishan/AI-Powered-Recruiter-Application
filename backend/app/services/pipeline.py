from app.services.ai_extractor import extract_resume_data
from app.services.matcher import generate_match
from app.db.connection import execute_write, execute_one, execute_returning
from app.core.logging import logger
import json


async def run_ai_pipeline(candidate_id: str, resume_text: str):
    """
    Background task: runs AI extraction and saves to DB.
    Called from the upload endpoint via BackgroundTasks.
    """
    logger.info("AI_PIPELINE_STARTED", candidate_id=candidate_id)

    # Update status to processing
    execute_write(
        "UPDATE candidates SET processing_status = %s, updated_at = NOW() WHERE id = %s",
        ("processing", candidate_id),
    )

    try:
        # Phase 3: AI Extraction
        extraction = await extract_resume_data(resume_text)

        # Phase 4: Save to DB using parameterized queries
        execute_write(
            """
            INSERT INTO ai_analysis
                (candidate_id, summary, extracted_skills, extracted_education,
                 extracted_experience, calculated_years_experience,
                 extracted_projects, extracted_certifications)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                candidate_id,
                extraction.summary,
                json.dumps(extraction.skills.model_dump()),
                json.dumps([e.model_dump() for e in extraction.education]),
                json.dumps([e.model_dump() for e in extraction.experience]),
                extraction.calculated_years_experience,
                json.dumps([p.model_dump() for p in extraction.projects]),
                json.dumps([c.model_dump() for c in extraction.certifications]),
            ),
        )

        # Update processing status
        execute_write(
            "UPDATE candidates SET processing_status = %s, updated_at = NOW() WHERE id = %s",
            ("complete", candidate_id),
        )

        logger.info("AI_PIPELINE_COMPLETE", candidate_id=candidate_id)

    except Exception as e:
        logger.error("AI_PIPELINE_FAILED", candidate_id=candidate_id, error=str(e))
        execute_write(
            "UPDATE candidates SET processing_status = %s, updated_at = NOW() WHERE id = %s",
            ("failed", candidate_id),
        )


async def run_match_pipeline(candidate_id: str, job_id: str):
    """
    Background task: runs AI matching between a candidate and a job.
    """
    logger.info(
        "MATCH_PIPELINE_STARTED", candidate_id=candidate_id, job_id=job_id
    )

    try:
        # Get candidate AI analysis
        analysis = execute_one(
            """
            SELECT summary, extracted_skills, extracted_education,
                   extracted_experience, calculated_years_experience,
                   extracted_projects, extracted_certifications
            FROM ai_analysis WHERE candidate_id = %s
            ORDER BY created_at DESC LIMIT 1
            """,
            (candidate_id,),
        )

        if not analysis:
            logger.error(
                "MATCH_PIPELINE_NO_ANALYSIS", candidate_id=candidate_id
            )
            return

        # Get job description
        job = execute_one(
            "SELECT id, title, raw_description, minimum_experience_years FROM job_descriptions WHERE id = %s",
            (job_id,),
        )

        if not job:
            logger.error("MATCH_PIPELINE_NO_JOB", job_id=job_id)
            return

        # Run matching engine
        result = await generate_match(
            candidate_profile=analysis,
            job_description=job,
        )

        # Save match result
        execute_write(
            """
            INSERT INTO match_records (candidate_id, job_id, match_score, fit_analysis, skill_mapping)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (candidate_id, job_id)
            DO UPDATE SET match_score = EXCLUDED.match_score,
                          fit_analysis = EXCLUDED.fit_analysis,
                          skill_mapping = EXCLUDED.skill_mapping,
                          review_status = 'pending',
                          matched_at = NOW()
            """,
            (
                candidate_id,
                job_id,
                result["match_score"],
                json.dumps(result["fit_analysis"]),
                json.dumps(result["skill_mapping"]),
            ),
        )

        logger.info(
            "MATCH_PIPELINE_COMPLETE",
            candidate_id=candidate_id,
            job_id=job_id,
            score=result["match_score"],
        )

    except Exception as e:
        logger.error(
            "MATCH_PIPELINE_FAILED",
            candidate_id=candidate_id,
            job_id=job_id,
            error=str(e),
        )
