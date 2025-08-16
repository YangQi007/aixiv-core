from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict, EmailStr, HttpUrl
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
    
    # New fields
    aixiv_id: Optional[str] = Field(None, max_length=50)
    doi: Optional[str] = Field(None, max_length=100)
    version: Optional[str] = Field("1.0", max_length=20)
    doc_type: str = Field(..., max_length=50)  # Document type (paper, preprint, review, etc.)

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


class ProfileUpdateRequest(BaseModel):
    user_id: str
    name: str
    title: Optional[str] = None
    affiliation: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None
    github: Optional[HttpUrl] = None
    twitter: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None
    avatar_url: Optional[str] = None


class ProfileResponse(BaseModel):
    id: int
    user_id: str
    name: str
    title: Optional[str]
    affiliation: Optional[str]
    location: Optional[str]
    bio: Optional[str]
    email: Optional[str]
    website: Optional[str]
    github_url: Optional[str]
    twitter_url: Optional[str]
    linkedin_url: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    message: str

class Score(BaseModel):
    novelty: confloat(ge=0, le=5) = Field(..., description="0–5")
    clarity: confloat(ge=0, le=5) = Field(..., description="0–5")
    significance: confloat(ge=0, le=5) = Field(..., description="0–5")
    technical: confloat(ge=0, le=5) = Field(..., description="0–5")

class ReviewIn(BaseModel):
    doi: constr(strip_whitespace=True, min_length=5, max_length=128)
    score: Score
    summary: str
    strengths: str
    weaknesses: str

class ReviewOut(BaseModel):
    code: int = 200
    message: str = "accepted"
    paper_id: str
    id: int

class Review(BaseModel):
    review_content: Dict
    status: int
    id: int
    reviewer: str
    like_count: int
    create_time: datetime