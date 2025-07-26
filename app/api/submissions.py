from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime
import tempfile
import requests as pyrequests
import fitz  # PyMuPDF for PDF extraction
import re

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
from app.config import settings
import boto3
from urllib.parse import urlparse

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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
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

@router.post("/extract-abstract")
async def extract_abstract(request: Request):
    data = await request.json()
    s3_url = data.get("s3_url")
    if not s3_url:
        return {"abstract": "No S3 URL provided."}

    # Parse S3 URL
    parsed = urlparse(s3_url)
    bucket = parsed.netloc.split(".")[0] if ".s3" in parsed.netloc else parsed.netloc
    key = parsed.path.lstrip("/")

    # Download the file from S3 using boto3
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region
    )
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            s3.download_fileobj(bucket, key, tmp)
            tmp_path = tmp.name
    except Exception as e:
        return {"abstract": f"Failed to download file from S3: {str(e)}"}

    # Try PDF extraction first
    abstract = None
    try:
        doc = fitz.open(tmp_path)
        text = "\n".join(page.get_text() for page in doc)
        # Stricter regex: stop at 'Keywords', double newline, or common section headings
        match = re.search(
            r'(?i)abstract\s*[:\n\r]+([\s\S]+?)(?=\n{2,}|(\n\s*(\d+\.\s*)?(keywords|introduction|background|methods|materials|results|discussion|conclusion|references|\\section))|$)',
            text
        )
        if match:
            abstract = match.group(1).strip()
        doc.close()
    except Exception:
        pass

    # If not PDF or no abstract found, try LaTeX
    if not abstract:
        try:
            with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            match = re.search(r'\\begin\{abstract\}(.+?)\\end\{abstract\}', content, re.DOTALL)
            if match:
                abstract = match.group(1).strip()
        except Exception:
            pass

    if not abstract:
        abstract = "Could not extract abstract from the uploaded file."

    return {"abstract": abstract}

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