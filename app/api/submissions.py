from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import logging

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
    max_retries = 3
    for attempt in range(max_retries):
        try:
            new_submission = create_submission(db=db, submission=submission)
            return SubmissionResponse(
                success=True, 
                submission_id=str(new_submission.id), 
                message="Paper submitted successfully!"
            )
        except IntegrityError as e:
            db.rollback() # Rollback the failed transaction
            if "ix_submissions_aixiv_id" in str(e) and attempt < max_retries - 1:
                logging.warning(f"Race condition for aixiv_id detected. Retrying... (Attempt {attempt + 1})")
                continue # Retry the loop
            else:
                logging.error(f"Error submitting paper after retries: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error submitting paper: {e}"
                )
        except Exception as e:
            db.rollback()
            logging.error(f"An unexpected error occurred: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred: {e}"
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
    try:
        submissions = get_submissions(db, skip=skip, limit=limit)
        return submissions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving submissions: {str(e)}"
        )

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