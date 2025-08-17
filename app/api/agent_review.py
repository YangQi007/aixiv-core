from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request

from app.crud import like_review, dislike_review, create_paper_review, get_reviews
from app.database import get_db
from app.schemas import ReviewOut, ReviewIn, Review
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api", tags=["agent_review"])

@router.post("/generate")
async def generate_token(oauth2_scheme: str):
    """
    This is a place hold for generate a jwt token for user to do the review upload
    """
    try:
        # verify the original jwt
        # payload = verify_jwt_token(token)
        # generate a jwt token for user to upload review
        # new_token = create_jwt_token({"user_id": user_id})
        token = ""
        return token
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating token: {str(e)}")


@router.post("/submit-review", response_model=ReviewOut)
async def submit_review(
        review: ReviewIn,
        request: Request,
        db: Session = Depends(get_db)
):
    """
    Save a place for JWT Auth
    """
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
            id=rec.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"submit failed: {str(e)}"
        )


@router.get("/get-review", response_model=List[Review])
async def get_review(
        paper_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[int] = None,
        db: Session = Depends(get_db)
):
    """
    Save a place for JWT Auth
    """

    reviews = get_reviews(db, paper_id, start_date, end_date, status)

    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for the given paper_id.")

    return reviews


@router.post("/like", response_model=ReviewOut)
async def like_review_endpoint(
        paper_id: str,
        review_id: int,
        db: Session = Depends(get_db)
):
    """
    Save a place for JWT Auth
    """

    review = like_review(db, review_id, paper_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")

    return ReviewOut(
        code=200,
        message="like updated",
        paper_id=review.paper_id,
        id=review.id,
    )


@router.post("/dislike", response_model=ReviewOut)
async def dislike_review_endpoint(
        paper_id: str,
        review_id: int,
        db: Session = Depends(get_db)
):
    """
    Save a place for JWT Auth
    """

    review = dislike_review(db, review_id, paper_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")

    return ReviewOut(
        code=200,
        message="dislike updated",
        paper_id=review.paper_id,
        id=review.id,
    )


def _get_client_ip(req: Request) -> str:
    xff = req.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    cip = req.headers.get("cf-connecting-ip")
    if cip:
        return cip
    return req.client.host if req.client else "0.0.0.0"
