import instructor
import google.generativeai as genai
from app.schemas.match import SemanticMappingResult, FitAnalysis
from app.core.config import settings
from app.core.logging import logger

genai.configure(api_key=settings.GEMINI_API_KEY)
client = instructor.from_gemini(
    client=genai.GenerativeModel(model_name=settings.AI_MODEL),
    mode=instructor.Mode.GEMINI_JSON,
)

# Scoring weights — deterministic math, not AI guesswork
WEIGHTS = {
    "skills": 0.50,
    "experience": 0.20,
    "education": 0.15,
    "projects": 0.10,
    "certifications": 0.05,
}


async def generate_match(candidate_profile: dict, job_description: dict) -> dict:
    """
    Step 1: AI does semantic synonym mapping (REST API == backend service == 0.9 match).
    Step 2: Math does the scoring. AI cannot inflate a score.
    """

    # --- Batch Semantic Mapping ---
    mapping_prompt = f"""
    Map each JD requirement to the closest candidate skill and assign a match confidence (0.0-1.0).
    Also evaluate experience match and education match.

    JD Requirements:
    {job_description['raw_description']}

    Candidate Profile:
    Skills: {candidate_profile.get('extracted_skills', {})}
    Experience: {candidate_profile.get('extracted_experience', [])}
    Education: {candidate_profile.get('extracted_education', [])}
    Certifications: {candidate_profile.get('extracted_certifications', [])}
    """

    mapping: SemanticMappingResult = client.chat.completions.create(
        response_model=SemanticMappingResult,
        max_retries=2,
        messages=[{"role": "user", "content": mapping_prompt}],
    )

    # --- Deterministic Score Calculation ---
    # Skills: average match confidence across all mapped requirements
    skill_score = (
        sum(m.match_confidence for m in mapping.skill_mappings)
        / len(mapping.skill_mappings)
        if mapping.skill_mappings
        else 0.0
    )

    # Experience: linear scale relative to JD minimum
    jd_min_years = job_description.get("minimum_experience_years", 0)
    candidate_years = float(
        candidate_profile.get("calculated_years_experience", 0)
    )
    experience_score = (
        min(candidate_years / max(jd_min_years, 1), 1.0)
        if jd_min_years
        else mapping.experience_match
    )

    education_score = mapping.education_match

    # Projects: presence and relevance ratio (0-1 based on how many skills overlap)
    projects = candidate_profile.get("extracted_projects", [])
    project_score = min(len(projects) / 5, 1.0)  # Normalize to 5 projects = full score

    # Certifications: bonus for each relevant cert, capped at 1.0
    certs = candidate_profile.get("extracted_certifications", [])
    cert_score = min(len(certs) / 3, 1.0)

    # Apply weights
    final_score = (
        WEIGHTS["skills"] * skill_score
        + WEIGHTS["experience"] * experience_score
        + WEIGHTS["education"] * education_score
        + WEIGHTS["projects"] * project_score
        + WEIGHTS["certifications"] * cert_score
    ) * 100  # Convert to percentage

    # --- AI Fit Analysis (narrative only — does NOT affect score) ---
    fit_prompt = f"""
    Given a match score of {final_score:.1f}%, write a brief fit analysis.
    Candidate skills: {candidate_profile.get('extracted_skills', {})}
    JD requirements: {job_description['raw_description'][:1000]}
    """

    fit: FitAnalysis = client.chat.completions.create(
        response_model=FitAnalysis,
        max_retries=2,
        messages=[{"role": "user", "content": fit_prompt}],
    )

    return {
        "match_score": round(final_score, 2),
        "fit_analysis": fit.model_dump(),
        "skill_mapping": [
            m.model_dump() for m in mapping.skill_mappings
        ],  # Store for auditability
    }
