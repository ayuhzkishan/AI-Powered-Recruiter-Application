from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class CandidateCreateSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v):
        cleaned = v.strip()
        if len(cleaned) < 1 or len(cleaned) > 100:
            raise ValueError("Name must be between 1 and 100 characters")
        return cleaned

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        import re
        cleaned = re.sub(r'[^\d\s\-\(\)\+]', '', v).strip()
        if len(cleaned) > 20:
            raise ValueError("Phone number too long")
        return cleaned


class CandidateResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    processing_status: str = "pending"
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class CandidateDetailResponse(CandidateResponse):
    raw_resume_text: Optional[str] = None
    resume_file_path: Optional[str] = None
    ai_analysis: Optional[dict] = None
