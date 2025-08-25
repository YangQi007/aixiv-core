import traceback
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request

from app.crud import create_paper_review, get_reviews, check_if_exist
from app.database import get_db
from app.schemas import SubmitReviewIn, Review, SubmitReviewOut, GetReviewOut, GetReviewIn
from app.constants import AgentType, DocType, ResponseCode, ReviewerConst
from sqlalchemy.orm import Session
from app.config import settings
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

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

        # Log input parameters (mask sensitive fields)
        try:
            masked_token = _mask_token(review.token)
            logger.info({
                "event": "submit-review:request",
                "client_ip": client_ip,
                "aixiv_id": review.aixiv_id,
                "version": review.version,
                "doc_type": review.doc_type,
                "reviewer": review.reviewer,
                "has_review_results": bool(review.review_results),
                "token": masked_token,
            })
        except Exception:
            # Avoid failing the request due to logging issues
            pass

        if settings.paper_exist_check:
            rec = check_if_exist(
                db=db, aixiv_id=review.aixiv_id, version=review.version, doc_type=review.doc_type
            )
            if rec is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Review submission with aixiv_id={review.aixiv_id} and version={review.version} and doc_type={review.doc_type} does not exist"
                )

        agent_type_val, doc_type_val = _resolve_agent_and_doc(
            reviewer=review.reviewer,
            doc_type=review.doc_type,
            token=review.token,
        )

        if settings.ip_limit_window_size > 0:
                start_time = datetime.now(timezone.utc) - timedelta(hours=settings.ip_limit_window_size)
                rec = get_reviews(db, review.aixiv_id, start_time, datetime.now(timezone.utc), review.version, client_ip, doc_type_val)
                if len(rec) > settings.ip_limit_frequency:
                    raise HTTPException(
                        status_code=429,
                        detail=f"Review submission with aixiv_id={review.aixiv_id} and version={review.version} and doc_type={review.doc_type} with ip={client_ip} has submitted too frequently, plz wait for {settings.ip_limit_window_size} hour to retry."
                    )

        rec = create_paper_review(
            db=db,
            payload=review,
            agent_type=agent_type_val,
            doc_type=doc_type_val,
            ip=client_ip
        )

        return SubmitReviewOut(
            code = ResponseCode.SUCCESS,
            aixiv_id=rec.aixiv_id,
            version=rec.version,
            id=rec.id
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error({
            "event": "submit-review:error",
            "aixiv_id": review.aixiv_id,
            "version": review.version,
            "doc_type": review.doc_type,
            "reviewer": review.reviewer,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
        })

        raise HTTPException(
            status_code=ResponseCode.INTERNAL_ERROR,
            detail="submit failed: internal server error"
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
        # Log input parameters for get-review
        try:
            logger.info({
                "event": "get-review:request",
                "aixiv_id": query.aixiv_id,
                "version": query.version,
                "start_date": query.start_date.isoformat() if query.start_date else None,
                "end_date": query.end_date.isoformat() if query.end_date else None,
            })
        except Exception:
            pass

        reviews = get_reviews(db, query.aixiv_id, query.start_date, query.end_date, query.version)

        reviews_list = [Review(
            aixiv_id=r.aixiv_id,
            version=r.version,
            review_results=r.review_results,
            create_time=r.create_time,
            reviewer=ReviewerConst.REVIEWERS_TYPE_MAP.get(r.agent_type, ReviewerConst.UNKNOWN_REVIEWER),
        ) for r in reviews]

        return GetReviewOut(
            review_list=reviews_list,
            code=ResponseCode.SUCCESS
        )
    except Exception as e:
        logger.info({
            "event": "get-review:request",
            "aixiv_id": query.aixiv_id,
            "version": query.version,
            "start_date": query.start_date.isoformat() if query.start_date else None,
            "end_date": query.end_date.isoformat() if query.end_date else None,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
        })

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


def _mask_token(token: Optional[str]) -> str | None:
    if not token:
        return None
    # Show only last 4 characters for debugging while masking the rest
    if len(token) <= 4:
        return "***" + token
    return "***" + token[-4:]


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
