from fastapi import APIRouter, HTTPException, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.api.deps import get_current_user
from app.schemas.job import JobCreateSchema, JobUpdateSchema
from app.db.connection import execute_returning, execute_one, execute_many, execute_write
from app.core.logging import log_security_event
import uuid as _uuid

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("", status_code=201)
async def create_job(
    payload: JobCreateSchema,
    current_user=Depends(get_current_user),
):
    """Create a new job description."""
    job = execute_returning(
        """
        INSERT INTO job_descriptions (title, department, raw_description, minimum_experience_years, created_by)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, title, department, status, raw_description, minimum_experience_years, created_at
        """,
        (
            payload.title,
            payload.department,
            payload.raw_description,
            payload.minimum_experience_years,
            str(current_user["id"]),
        ),
    )

    log_security_event("JOB_CREATED", user_id=str(current_user["id"]),
                       details={"job_id": str(job["id"])})

    return {
        "id": str(job["id"]),
        "title": job["title"],
        "department": job.get("department"),
        "status": job["status"],
        "raw_description": job["raw_description"],
        "minimum_experience_years": job["minimum_experience_years"],
        "created_at": str(job["created_at"]) if job.get("created_at") else None,
    }


@router.get("")
async def list_jobs(current_user=Depends(get_current_user)):
    """List all job descriptions."""
    rows = execute_many(
        """
        SELECT id, title, department, status, raw_description,
               minimum_experience_years, created_at
        FROM job_descriptions
        ORDER BY created_at DESC
        """
    )
    return [
        {
            "id": str(row["id"]),
            "title": row["title"],
            "department": row.get("department"),
            "status": row["status"],
            "raw_description": row["raw_description"],
            "minimum_experience_years": row["minimum_experience_years"],
            "created_at": str(row["created_at"]) if row.get("created_at") else None,
        }
        for row in rows
    ]


@router.get("/{job_id}")
async def get_job(job_id: str, current_user=Depends(get_current_user)):
    """Get a single job description with its match records."""
    try:
        _uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    job = execute_one(
        """
        SELECT id, title, department, status, raw_description,
               minimum_experience_years, created_at
        FROM job_descriptions WHERE id = %s
        """,
        (job_id,),
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get matches for this job
    matches = execute_many(
        """
        SELECT mr.id, mr.candidate_id, mr.match_score, mr.fit_analysis,
               mr.skill_mapping, mr.review_status, mr.matched_at,
               c.first_name, c.last_name, c.email
        FROM match_records mr
        JOIN candidates c ON c.id = mr.candidate_id
        WHERE mr.job_id = %s
        ORDER BY mr.match_score DESC
        """,
        (job_id,),
    )

    return {
        "id": str(job["id"]),
        "title": job["title"],
        "department": job.get("department"),
        "status": job["status"],
        "raw_description": job["raw_description"],
        "minimum_experience_years": job["minimum_experience_years"],
        "created_at": str(job["created_at"]) if job.get("created_at") else None,
        "matches": [
            {
                "id": str(m["id"]),
                "candidate_id": str(m["candidate_id"]),
                "candidate_name": f"{m['first_name']} {m['last_name']}",
                "candidate_email": m["email"],
                "match_score": float(m["match_score"]),
                "fit_analysis": m["fit_analysis"],
                "skill_mapping": m["skill_mapping"],
                "review_status": m["review_status"],
                "matched_at": str(m["matched_at"]) if m.get("matched_at") else None,
            }
            for m in matches
        ],
    }


@router.put("/{job_id}")
async def update_job(
    job_id: str,
    payload: JobUpdateSchema,
    current_user=Depends(get_current_user),
):
    """Update a job description."""
    try:
        _uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    existing = execute_one(
        "SELECT id FROM job_descriptions WHERE id = %s", (job_id,)
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Job not found")

    # Build dynamic update query
    updates = []
    values = []
    data = payload.model_dump(exclude_none=True)
    for field, value in data.items():
        updates.append(f"{field} = %s")
        values.append(value)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    updates.append("updated_at = NOW()")
    values.append(job_id)

    execute_write(
        f"UPDATE job_descriptions SET {', '.join(updates)} WHERE id = %s",
        tuple(values),
    )

    return {"message": "Job updated successfully", "job_id": job_id}


@router.delete("/{job_id}")
async def delete_job(job_id: str, current_user=Depends(get_current_user)):
    """Delete a job description."""
    try:
        _uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    existing = execute_one(
        "SELECT id FROM job_descriptions WHERE id = %s", (job_id,)
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Job not found")

    execute_write("DELETE FROM job_descriptions WHERE id = %s", (job_id,))
    log_security_event("JOB_DELETED", user_id=str(current_user["id"]),
                       details={"job_id": job_id})

    return {"message": "Job deleted successfully"}
