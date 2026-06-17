from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.api.deps import get_current_user
from app.services.pipeline import run_match_pipeline
from app.db.connection import execute_one, execute_many
from app.core.logging import log_security_event
import uuid as _uuid

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/{candidate_id}/match/{job_id}", status_code=202)
@limiter.limit("30/minute")
async def trigger_match(
    candidate_id: str,
    job_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
):
    """Trigger AI matching between a candidate and a job."""
    # Validate UUIDs to prevent injection
    try:
        _uuid.UUID(candidate_id)
        _uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # Verify resources exist (A01)
    candidate = execute_one(
        "SELECT id, processing_status FROM candidates WHERE id = %s",
        (candidate_id,),
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if candidate["processing_status"] != "complete":
        raise HTTPException(
            status_code=400,
            detail="Candidate resume analysis is not complete yet",
        )

    job = execute_one(
        "SELECT id FROM job_descriptions WHERE id = %s", (job_id,)
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    background_tasks.add_task(run_match_pipeline, candidate_id, job_id)

    log_security_event(
        "MATCH_TRIGGERED",
        user_id=str(current_user["id"]),
        details={"candidate_id": candidate_id, "job_id": job_id},
    )

    return {"status": "matching", "candidate_id": candidate_id, "job_id": job_id}


@router.get("")
async def list_all_matches(current_user=Depends(get_current_user)):
    """List all match records."""
    rows = execute_many(
        """
        SELECT mr.id, mr.candidate_id, mr.job_id, mr.match_score,
               mr.fit_analysis, mr.skill_mapping, mr.review_status, mr.matched_at,
               c.first_name, c.last_name, c.email as candidate_email,
               jd.title as job_title, jd.department
        FROM match_records mr
        JOIN candidates c ON c.id = mr.candidate_id
        JOIN job_descriptions jd ON jd.id = mr.job_id
        ORDER BY mr.match_score DESC
        """
    )
    return [
        {
            "id": str(row["id"]),
            "candidate_id": str(row["candidate_id"]),
            "job_id": str(row["job_id"]),
            "candidate_name": f"{row['first_name']} {row['last_name']}",
            "candidate_email": row["candidate_email"],
            "job_title": row["job_title"],
            "department": row.get("department"),
            "match_score": float(row["match_score"]),
            "fit_analysis": row["fit_analysis"],
            "skill_mapping": row["skill_mapping"],
            "review_status": row["review_status"],
            "matched_at": str(row["matched_at"]) if row.get("matched_at") else None,
        }
        for row in rows
    ]


@router.get("/job/{job_id}")
async def list_matches_for_job(job_id: str, current_user=Depends(get_current_user)):
    """List all matches for a specific job, sorted by score."""
    try:
        _uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    rows = execute_many(
        """
        SELECT mr.id, mr.candidate_id, mr.match_score,
               mr.fit_analysis, mr.skill_mapping, mr.review_status, mr.matched_at,
               c.first_name, c.last_name, c.email
        FROM match_records mr
        JOIN candidates c ON c.id = mr.candidate_id
        WHERE mr.job_id = %s
        ORDER BY mr.match_score DESC
        """,
        (job_id,),
    )
    return [
        {
            "id": str(row["id"]),
            "candidate_id": str(row["candidate_id"]),
            "candidate_name": f"{row['first_name']} {row['last_name']}",
            "candidate_email": row["email"],
            "match_score": float(row["match_score"]),
            "fit_analysis": row["fit_analysis"],
            "skill_mapping": row["skill_mapping"],
            "review_status": row["review_status"],
            "matched_at": str(row["matched_at"]) if row.get("matched_at") else None,
        }
        for row in rows
    ]


@router.put("/{match_id}/review")
async def update_review_status(
    match_id: str,
    status: str,
    current_user=Depends(get_current_user),
):
    """Update the review status of a match (pending/shortlisted/rejected)."""
    try:
        _uuid.UUID(match_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    if status not in ("pending", "shortlisted", "rejected"):
        raise HTTPException(
            status_code=400,
            detail="Status must be pending, shortlisted, or rejected",
        )

    match = execute_one(
        "SELECT id FROM match_records WHERE id = %s", (match_id,)
    )
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    from app.db.connection import execute_write

    execute_write(
        "UPDATE match_records SET review_status = %s WHERE id = %s",
        (status, match_id),
    )

    return {"message": "Review status updated", "match_id": match_id, "status": status}
