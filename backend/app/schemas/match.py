from pydantic import BaseModel, Field
from typing import List, Optional


class SkillMapping(BaseModel):
    jd_requirement: str = Field(..., max_length=200)
    candidate_skill: str = Field(..., max_length=200)
    match_confidence: float = Field(..., ge=0.0, le=1.0)


class SemanticMappingResult(BaseModel):
    skill_mappings: List[SkillMapping] = Field(default_factory=list, max_length=100)
    experience_match: float = Field(..., ge=0.0, le=1.0)
    education_match: float = Field(..., ge=0.0, le=1.0)


class FitAnalysis(BaseModel):
    strengths: List[str] = Field(default_factory=list, max_length=10)
    gaps: List[str] = Field(default_factory=list, max_length=10)
    reasoning: str = Field(..., max_length=1000)


class MatchResponse(BaseModel):
    id: str
    candidate_id: str
    job_id: str
    match_score: float
    fit_analysis: Optional[dict] = None
    skill_mapping: Optional[list] = None
    review_status: str = "pending"
    matched_at: Optional[str] = None
    candidate_name: Optional[str] = None
    job_title: Optional[str] = None
