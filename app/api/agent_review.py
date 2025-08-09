from fastapi import APIRouter, Depends, HTTPException, status, Request

from app.crud import create_submission, get_submission, get_submissions, create_paper_review
from app.database import get_db
from app.schemas import ReviewOut, ReviewIn
from sqlalchemy.orm import Session
from app.services.s3_service import s3_service
from app.config import settings
import boto3
from urllib.parse import urlparse

router = APIRouter(prefix="/api", tags=["agent_review"])

@router.post("/submit-review", response_model=ReviewOut)
async def submit_review(
    review: ReviewIn,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        client_ip = _get_client_ip(request)
        rec = create_paper_review(
            db=db,
            payload=review,
            client_ip=client_ip,
            reviewer_name="Anonymous Reviewer",
            user_id=None,
            status=2,
        )
        return ReviewOut(
            code=200,
            message="accepted",
            paper_id=rec.paper_id,
            review_id=rec.review_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"submit failed: {str(e)}"
        )

def _get_client_ip(req: Request) -> str:
    xff = req.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    cip = req.headers.get("cf-connecting-ip")
    if cip:
        return cip
    return req.client.host if req.client else "0.0.0.0"