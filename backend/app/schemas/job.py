from pydantic import BaseModel, field_validator
from typing import Optional


class JobCreateSchema(BaseModel):
    title: str
    department: Optional[str] = None
    raw_description: str
    minimum_experience_years: int = 0

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        cleaned = v.strip()
        if len(cleaned) < 3 or len(cleaned) > 200:
            raise ValueError("Title must be between 3 and 200 characters")
        return cleaned

    @field_validator("raw_description")
    @classmethod
    def validate_description(cls, v):
        cleaned = v.strip()
        if len(cleaned) < 50:
            raise ValueError("Job description must be at least 50 characters")
        if len(cleaned) > 10000:
            raise ValueError("Job description must be under 10,000 characters")
        return cleaned

    @field_validator("minimum_experience_years")
    @classmethod
    def validate_experience(cls, v):
        if v < 0 or v > 50:
            raise ValueError("Experience must be between 0 and 50 years")
        return v


class JobUpdateSchema(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    raw_description: Optional[str] = None
    minimum_experience_years: Optional[int] = None
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in ("draft", "active", "closed"):
            raise ValueError("Status must be draft, active, or closed")
        return v


class JobResponse(BaseModel):
    id: str
    title: str
    department: Optional[str] = None
    status: str = "draft"
    raw_description: str
    minimum_experience_years: int = 0
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
