from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

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
    
    class Config:
        from_attributes = True

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