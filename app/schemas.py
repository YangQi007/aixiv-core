import json

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict, EmailStr, HttpUrl
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, confloat, constr
from typing import Optional, Literal
from pydantic import BaseModel, Field, constr, validator
from pydantic.types import Json

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

class SubmitReviewIn(BaseModel):
    code: int
    aixiv_id: constr(strip_whitespace=True, min_length=5, max_length=128)
    version: constr(strip_whitespace=True, min_length=1, max_length=45)
    review_results: dict
    doc_type: Literal["proposal", "paper"]
    reviewer: Literal["agent", "human"]
    token: Optional[str] = None

    @field_validator("review_results", mode="before")
    def validate_json(cls, v):
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
            except Exception:
                raise ValueError("review_results must be a valid JSON string")
            if not isinstance(parsed, dict):
                raise ValueError("review_results must be a JSON object")
            return parsed
        raise ValueError("review_results must be a dict or JSON string")

class SubmitReviewOut(BaseModel):
    code: int
    aixiv_id: str
    version: str
    id: int

class Review(BaseModel):
    review_results: Dict
    version: str
    aixiv_id: str
    create_time: datetime
    reviewer: str

class GetReviewIn(BaseModel):
    aixiv_id: str
    version: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class GetReviewOut(BaseModel):
    review_list: List[Review]
    code: int