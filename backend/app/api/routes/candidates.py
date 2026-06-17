from fastapi import APIRouter, UploadFile, File, Form, Depends, BackgroundTasks, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.api.deps import get_current_user
from app.services.extractor import validate_file, extract_text, quality_check, FileValidationError
from app.services.storage import storage_service
from app.services.pipeline import run_ai_pipeline
from app.core.logging import log_security_event
from app.db.connection import execute_returning, execute_one, execute_many, execute_write

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/upload", status_code=202)
@limiter.limit("10/minute")  # Prevent abuse of AI-backed endpoint (A04)
async def upload_resume(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    current_user=Depends(get_current_user),  # Authentication required (A01)
):
    content = await file.read()

    log_security_event(
        "FILE_UPLOAD_ATTEMPT",
        user_id=str(current_user["id"]),
        details={"filename": file.filename, "size": len(content)},
    )

    # --- Phase 1: Validate ---
    try:
        mime_type = validate_file(content, file.filename)
    except FileValidationError as e:
        log_security_event(
            "FILE_REJECTED",
            user_id=str(current_user["id"]),
            details={"reason": str(e), "filename": file.filename},
        )
        raise HTTPException(status_code=422, detail=str(e))

    # --- Phase 2: Extract & Quality Check ---
    try:
        raw_text = extract_text(content, mime_type)
        clean_text = quality_check(raw_text)
    except FileValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # --- DB: Create Candidate Record ---
    candidate = execute_returning(
        """
        INSERT INTO candidates (first_name, last_name, email, phone, raw_resume_text, created_by, processing_status)
        VALUES (%s, %s, %s, %s, %s, %s, 'processing')
        ON CONFLICT (email) DO UPDATE SET
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            phone = EXCLUDED.phone,
            raw_resume_text = EXCLUDED.raw_resume_text,
            processing_status = 'processing'
        RETURNING id, first_name, last_name, email, processing_status, created_at
        """,
        (first_name, last_name, email, phone, clean_text, str(current_user["id"])),
    )

    # Save file with UUID-based path
    file_path = storage_service.save_file(
        str(candidate["id"]), content, file.filename
    )
    execute_write(
        "UPDATE candidates SET resume_file_path = %s WHERE id = %s",
        (file_path, str(candidate["id"])),
    )

    # --- Phase 3 & 4: Trigger AI as background task (no timeout) ---
    background_tasks.add_task(
        run_ai_pipeline,
        candidate_id=str(candidate["id"]),
        resume_text=clean_text,
    )

    log_security_event(
        "FILE_UPLOAD_SUCCESS",
        user_id=str(current_user["id"]),
        details={"candidate_id": str(candidate["id"])},
    )

    return {"candidate_id": str(candidate["id"]), "status": "processing"}


@router.get("")
async def list_candidates(current_user=Depends(get_current_user)):
    """List all candidates."""
    rows = execute_many(
        """
        SELECT c.id, c.first_name, c.last_name, c.email, c.phone,
               c.processing_status, c.created_at,
               a.summary, a.extracted_skills, a.calculated_years_experience
        FROM candidates c
        LEFT JOIN LATERAL (
            SELECT summary, extracted_skills, calculated_years_experience
            FROM ai_analysis
            WHERE candidate_id = c.id
            ORDER BY created_at DESC
            LIMIT 1
        ) a ON true
        ORDER BY c.created_at DESC
        """
    )
    result = []
    for row in rows:
        result.append({
            "id": str(row["id"]),
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "email": row["email"],
            "phone": row.get("phone"),
            "processing_status": row["processing_status"],
            "created_at": str(row["created_at"]) if row.get("created_at") else None,
            "summary": row.get("summary"),
            "skills": row.get("extracted_skills"),
            "years_experience": float(row["calculated_years_experience"]) if row.get("calculated_years_experience") else None,
        })
    return result


@router.get("/{candidate_id}")
async def get_candidate(candidate_id: str, current_user=Depends(get_current_user)):
    """Get detailed candidate profile with AI analysis."""
    import uuid as _uuid
    try:
        _uuid.UUID(candidate_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    candidate = execute_one(
        """
        SELECT id, first_name, last_name, email, phone, raw_resume_text,
               resume_file_path, processing_status, created_at
        FROM candidates WHERE id = %s
        """,
        (candidate_id,),
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Get AI analysis
    analysis = execute_one(
        """
        SELECT summary, extracted_skills, extracted_education,
               extracted_experience, calculated_years_experience,
               extracted_projects, extracted_certifications, created_at
        FROM ai_analysis WHERE candidate_id = %s
        ORDER BY created_at DESC LIMIT 1
        """,
        (candidate_id,),
    )

    # Get match records
    matches = execute_many(
        """
        SELECT mr.id, mr.job_id, mr.match_score, mr.fit_analysis,
               mr.skill_mapping, mr.review_status, mr.matched_at,
               jd.title as job_title
        FROM match_records mr
        JOIN job_descriptions jd ON jd.id = mr.job_id
        WHERE mr.candidate_id = %s
        ORDER BY mr.match_score DESC
        """,
        (candidate_id,),
    )

    return {
        "id": str(candidate["id"]),
        "first_name": candidate["first_name"],
        "last_name": candidate["last_name"],
        "email": candidate["email"],
        "phone": candidate.get("phone"),
        "processing_status": candidate["processing_status"],
        "created_at": str(candidate["created_at"]) if candidate.get("created_at") else None,
        "ai_analysis": {
            "summary": analysis["summary"],
            "skills": analysis["extracted_skills"],
            "education": analysis["extracted_education"],
            "experience": analysis["extracted_experience"],
            "years_experience": float(analysis["calculated_years_experience"]) if analysis.get("calculated_years_experience") else None,
            "projects": analysis["extracted_projects"],
            "certifications": analysis["extracted_certifications"],
        } if analysis else None,
        "matches": [
            {
                "id": str(m["id"]),
                "job_id": str(m["job_id"]),
                "job_title": m["job_title"],
                "match_score": float(m["match_score"]),
                "fit_analysis": m["fit_analysis"],
                "skill_mapping": m["skill_mapping"],
                "review_status": m["review_status"],
                "matched_at": str(m["matched_at"]) if m.get("matched_at") else None,
            }
            for m in matches
        ],
    }


@router.get("/{candidate_id}/status")
async def get_candidate_status(candidate_id: str, current_user=Depends(get_current_user)):
    """Check processing status for polling."""
    import uuid as _uuid
    try:
        _uuid.UUID(candidate_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    candidate = execute_one(
        "SELECT processing_status FROM candidates WHERE id = %s",
        (candidate_id,),
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    return {"candidate_id": candidate_id, "status": candidate["processing_status"]}
