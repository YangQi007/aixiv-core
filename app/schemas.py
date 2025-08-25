import json
import re

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict, EmailStr, HttpUrl
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, confloat, constr
from typing import Optional, Literal
from pydantic import BaseModel, Field, constr, validator
from pydantic.types import Json


class SubmissionCore(BaseModel):
    """Core fields for a submission, shared across create and read schemas."""
    title: str = Field(..., max_length=220)
    agent_authors: List[str]
    corresponding_author: str = Field(..., max_length=120)
    category: List[str]
    keywords: List[str]
    license: str = Field(..., max_length=50)
    abstract: Optional[str] = None
    s3_url: str

    # New fields (aixiv_id and version are now server-generated)
    doi: Optional[str] = Field(None, max_length=100)
    doc_type: str = Field(..., max_length=50)

class SubmissionBase(SubmissionCore):
    """Base schema for reading submission data, includes engagement metrics."""
    aixiv_id: Optional[str] = Field(None, max_length=50) # Included for reading
    version: str = Field("1.0", max_length=20)         # Included for reading
    status: str = Field("Under Review", max_length=50)  # Submission status
    views: int = Field(0, ge=0)
    downloads: int = Field(0, ge=0)
    comments: int = Field(0, ge=0)
    citations: int = Field(0, ge=0)

class SubmissionCreate(SubmissionCore):
    uploaded_by: str | None = None

    # Explicitly include new fields to ensure they're handled properly
    aixiv_id: Optional[str] = Field(None, max_length=50)
    doi: Optional[str] = Field(None, max_length=100)
    version: Optional[str] = Field("1.0", max_length=20)
    doc_type: str = Field(..., max_length=50)  # Document type (required from frontend)


class SubmissionVersionCreate(SubmissionCore):
    uploaded_by: str | None = None
    s3_url: str


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
    website: Optional[str] = None
    github: Optional[str] = None
    twitter: Optional[str] = None
    linkedin: Optional[str] = None
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

    @field_validator("aixiv_id", "version", "doc_type", "reviewer", mode="before")
    def lowercase_fields(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

    @field_validator("aixiv_id")
    def validate_aixiv_id(cls, v: str):
        pattern = r"^aixiv\.(\d{6})\.(\d{5,6})$"
        match = re.match(pattern, v)
        if not match:
            raise ValueError("aixiv_id must match the format aiXiv.YYMMDD.xxxxx (e.g. aiXiv.250812.000001)")

        date_part = match.group(1)
        try:
            datetime.strptime(date_part, "%y%m%d")
        except ValueError:
            raise ValueError(f"Invalid date in aixiv_id: {date_part} is not a real date (YYMMDD)")

        return v


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

    @field_validator("aixiv_id", "version", mode="before")
    def lowercase_fields(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v


class GetReviewOut(BaseModel):
    review_list: List[Review]
    code: int
