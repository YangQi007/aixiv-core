from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, confloat, constr

class SubmissionBase(BaseModel):
    title: str = Field(..., max_length=220)
    agent_authors: List[str]
    corresponding_author: str = Field(..., max_length=120)
    category: List[str]
    keywords: List[str]
    license: str = Field(..., max_length=50)
    abstract: Optional[str] = None
    s3_url: str

class SubmissionCreate(SubmissionBase):
    uploaded_by: str = Field(..., max_length=64)

class SubmissionDB(SubmissionBase):
    id: int
    uploaded_by: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UploadUrlRequest(BaseModel):
    filename: str

class UploadUrlResponse(BaseModel):
    upload_url: str
    file_key: str
    s3_url: str
    content_type: str
    file_extension: str

class SubmissionResponse(BaseModel):
    success: bool
    submission_id: str
    message: str

class Score(BaseModel):
    novelty: confloat(ge=0, le=5) = Field(..., description="0–5")
    clarity: confloat(ge=0, le=5) = Field(..., description="0–5")
    significance: confloat(ge=0, le=5) = Field(..., description="0–5")
    technical: confloat(ge=0, le=5) = Field(..., description="0–5")

class ReviewIn(BaseModel):
    doi: constr(strip_whitespace=True, min_length=5, max_length=128)
    score: Score
    summary: str = Field(..., min_length=1, max_length=8000)
    strengths: str = Field(..., min_length=1, max_length=8000)
    weaknesses: str = Field(..., min_length=1, max_length=8000)

class ReviewOut(BaseModel):
    code: int = 200
    message: str = "accepted"
    paper_id: str
