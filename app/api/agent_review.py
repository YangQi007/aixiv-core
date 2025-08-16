from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request

from app.crud import create_paper_review, get_reviews
from app.database import get_db
from app.schemas import SubmitReviewIn, Review, SubmitReviewOut, GetReviewOut, GetReviewIn
from app.constants import AgentType, DocType, ResponseCode
from sqlalchemy.orm import Session
from app.config import settings

router = APIRouter(prefix="/api", tags=["agent_review"])


@router.post("/submit-review", response_model=SubmitReviewOut)
async def submit_review(
        review: SubmitReviewIn,
        request: Request,
        db: Session = Depends(get_db)
):
    """
    Save a place for JWT Auth
    """
    try:
        client_ip = _get_client_ip(request)

        agent_type_val, doc_type_val = _resolve_agent_and_doc(
            reviewer=review.reviewer,
            doc_type=review.doc_type,
            token=review.token,
        )

        rec = create_paper_review(
            db=db,
            payload=review,
            agent_type=agent_type_val,
            doc_type=doc_type_val
        )

        return SubmitReviewOut(
            code = ResponseCode.SUCCESS,
            aixiv_id=rec.aixiv_id,
            version=rec.version,
            id=rec.id
        )
    except Exception as e:
        raise HTTPException(
            status_code = ResponseCode.INTERNAL_ERROR,
            detail=f"submit failed: {str(e)}"
        )


@router.post("/get-review", response_model=GetReviewOut)
async def get_review(
        query: GetReviewIn,
        db: Session = Depends(get_db)
):
    """
    Save a place for JWT Auth
    """
    try:
        reviews = get_reviews(db, query.aixiv_id, query.start_date, query.end_date, query.version)
        return GetReviewOut(
            review_list=reviews,
            code=ResponseCode.SUCCESS
        )
    except Exception as e:
        raise HTTPException(
            status_code = ResponseCode.INTERNAL_ERROR,
            detail=f"query failed: {str(e)}"
        )

def _get_client_ip(req: Request) -> str:
    xff = req.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    cip = req.headers.get("cf-connecting-ip")
    if cip:
        return cip
    return req.client.host if req.client else "0.0.0.0"


def _map_reviewer_to_agent_type(reviewer: str) -> int:
    if reviewer == AgentType.agent.name:
        return AgentType.agent.value
    if reviewer == AgentType.human.name:
        return AgentType.human.value
    raise HTTPException(status_code=ResponseCode.BAD_REQUEST, detail="Invalid reviewer; must be 'Agent' or 'Human'")


def _normalize_doc_type(doc_type: str) -> str:
    if doc_type == DocType.paper.name:
        return DocType.paper.value
    if doc_type == DocType.proposal.name:
        return DocType.proposal.value
    raise HTTPException(status_code=ResponseCode.BAD_REQUEST, detail="Invalid doc_type; must be 'paper' or 'proposal'")


def _resolve_agent_and_doc(*, reviewer: str, doc_type: str, token: str | None) -> tuple[int, int]:
    if token:
        if token != settings.auth_token:
            raise HTTPException(status_code=ResponseCode.UNAUTHORIZED, detail="Invalid token")
        agent_type_val = AgentType.official.value
    else:
        agent_type_val = _map_reviewer_to_agent_type(reviewer)

    doc_type_val = _normalize_doc_type(doc_type)
    return int(agent_type_val), int(doc_type_val)
