from sqlalchemy import select, func, text
from sqlalchemy.orm import Session
from app.models import Submission, PaperReview
from app.schemas import SubmissionCreate, ReviewIn
from typing import List, Optional


def create_submission(db: Session, submission: SubmissionCreate) -> Submission:
    """
    Create a new submission in the database
    """
    db_submission = Submission(
        title=submission.title,
        agent_authors=submission.agent_authors,
        corresponding_author=submission.corresponding_author,
        category=submission.category,
        keywords=submission.keywords,
        license=submission.license,
        abstract=submission.abstract,
        s3_url=submission.s3_url,
        uploaded_by=submission.uploaded_by
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission


def get_submission(db: Session, submission_id: int) -> Optional[Submission]:
    """
    Get a submission by ID
    """
    return db.query(Submission).filter(Submission.id == submission_id).first()


def get_submissions(db: Session, skip: int = 0, limit: int = 100) -> List[Submission]:
    """
    Get all submissions with pagination
    """
    return db.query(Submission).offset(skip).limit(limit).all()


def get_submissions_by_user(db: Session, uploaded_by: str, skip: int = 0, limit: int = 100) -> List[Submission]:
    """
    Get submissions by user ID
    """
    return db.query(Submission).filter(Submission.uploaded_by == uploaded_by).offset(skip).limit(limit).all()


def update_submission(db: Session, submission_id: int, submission_data: dict) -> Optional[Submission]:
    """
    Update a submission
    """
    db_submission = get_submission(db, submission_id)
    if db_submission:
        for key, value in submission_data.items():
            if hasattr(db_submission, key):
                setattr(db_submission, key, value)
        db.commit()
        db.refresh(db_submission)
    return db_submission


def delete_submission(db: Session, submission_id: int) -> bool:
    """
    Delete a submission
    """
    db_submission = get_submission(db, submission_id)
    if db_submission:
        db.delete(db_submission)
        db.commit()
        return True
    return False


def create_paper_review(
        db: Session,
        payload: ReviewIn,
        client_ip: str | None = None,
        reviewer_name: str | None = "Anonymous Reviewer",
        user_id: str | None = None,
        status: int = 2,
) -> PaperReview:
    rec = PaperReview(
        paper_id=payload.doi,
        review=payload.model_dump(),
        status=status,
        ip=client_ip,
        reviewer=reviewer_name or "Anonymous Reviewer",
        user_id=user_id,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec
