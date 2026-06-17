from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class SkillSet(BaseModel):
    hard: List[str] = Field(default_factory=list)
    soft: List[str] = Field(default_factory=list)

    @field_validator("hard", "soft", mode="before")
    @classmethod
    def sanitize_skills(cls, v):
        return [str(s)[:100].strip() for s in v if s]


class EducationEntry(BaseModel):
    degree: Optional[str] = Field(None)
    institution: Optional[str] = Field(None)
    year: Optional[int] = Field(None)
    gpa: Optional[float] = Field(None)


class ExperienceEntry(BaseModel):
    title: Optional[str] = Field(None)
    company: Optional[str] = Field(None)
    duration_months: Optional[int] = Field(None)


class ProjectEntry(BaseModel):
    name: Optional[str] = Field(None)
    description: Optional[str] = Field(None)
    technologies: List[str] = Field(default_factory=list)


class CertificationEntry(BaseModel):
    name: Optional[str] = Field(None)
    issuer: Optional[str] = Field(None)
    year: Optional[int] = Field(None)


class ResumeExtraction(BaseModel):
    """
    instructor forces the LLM to return data matching exactly this schema.
    If the LLM deviates, instructor retries automatically up to max_retries.
    """
    summary: str = Field(
        ...,
        description="2-3 sentence professional summary of the candidate",
    )
    skills: SkillSet
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    calculated_years_experience: float = Field(
        ...,
        description="Total years of professional experience",
    )
    projects: List[ProjectEntry] = Field(default_factory=list)
    certifications: List[CertificationEntry] = Field(default_factory=list)
