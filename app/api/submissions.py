from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from app.database import get_db
from app.schemas import (
    SubmissionCreate, 
    SubmissionResponse, 
    UploadUrlRequest, 
    UploadUrlResponse,
    SubmissionDB
)
from app.crud import create_submission, get_submission, get_submissions
from app.services.s3_service import s3_service

router = APIRouter(prefix="/api", tags=["submissions"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@router.post("/get-upload-url", response_model=UploadUrlResponse)
async def get_upload_url(request: UploadUrlRequest):
    """
    Generate a pre-signed URL for uploading a file to S3
    """
    try:
        result = s3_service.generate_upload_url(request.filename)
        return UploadUrlResponse(**result)
    except ValueError as e:
        # Validation errors should return 400, not 500
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Only unexpected errors should return 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating upload URL: {str(e)}"
        )

@router.post("/submit", response_model=SubmissionResponse)
async def submit_paper(
    submission: SubmissionCreate,
    db: Session = Depends(get_db)
):
    """
    Submit a paper with metadata to the database
    """
    try:
        # Validate that the S3 URL exists (optional check)
        # You might want to verify the file actually exists in S3
        
        # Create submission in database
        db_submission = create_submission(db, submission)
        
        # Generate a submission ID for the response
        submission_id = f"SUB-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        return SubmissionResponse(
            success=True,
            submission_id=submission_id,
            message="Paper submitted successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting paper: {str(e)}"
        )

@router.get("/submissions", response_model=List[SubmissionDB])
async def list_submissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all submissions with pagination
    """
    submissions = get_submissions(db, skip=skip, limit=limit)
    return submissions

@router.get("/submissions/{submission_id}", response_model=SubmissionDB)
async def get_submission_by_id(
    submission_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific submission by ID
    """
    submission = get_submission(db, submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    return submission 