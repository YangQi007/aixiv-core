from datetime import datetime

from PIL.ImageChops import constant
from sqlalchemy.orm import Session
from app.models import Submission, PaperReview
from app.schemas import SubmissionCreate, SubmitReviewIn, Review
from typing import List, Optional, Any

from app.models import Submission, UserProfile
from app.schemas import SubmissionCreate
from typing import List, Optional, Dict
from app.constants import AgentType, DocType, ReviewerConst


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


def get_profile_by_user_id(db: Session, user_id: str) -> Optional[UserProfile]:
    """
    Get a user profile by user ID
    """
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()


def create_or_update_profile(db: Session, profile_data: Dict) -> UserProfile:
    """
    Create or update a user profile
    """
    user_id = profile_data.get('user_id')
    existing_profile = get_profile_by_user_id(db, user_id)

    # Get valid UserProfile columns
    valid_columns = UserProfile.__table__.columns.keys()

    # Filter profile_data to only include valid columns
    filtered_data = {k: v for k, v in profile_data.items() if k in valid_columns}

    if existing_profile:
        # Update existing profile
        for key, value in filtered_data.items():
            if value is not None:
                setattr(existing_profile, key, value)
        db.commit()
        db.refresh(existing_profile)
        return existing_profile
    else:
        # Create new profile with filtered data
        new_profile = UserProfile(**filtered_data)
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        return new_profile
    return False


def create_paper_review(
        db: Session,
        payload: SubmitReviewIn,
        agent_type: int = AgentType.agent.value,
        doc_type: int = DocType.paper.value
) -> PaperReview:
    rec = PaperReview(
        aixiv_id = payload.aixiv_id,
        version = payload.version,
        review_results = payload.review_results,
        agent_type = agent_type,
        doc_type = doc_type
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def get_reviews(
        db: Session,
        aixiv_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        version: Optional[str] = None
) -> list[Review]:
    query = db.query(PaperReview).filter(PaperReview.aixiv_id == aixiv_id)
    if start_date:
        query = query.filter(PaperReview.create_time >= start_date)
    if end_date:
        query = query.filter(PaperReview.create_time <= end_date)
    if version is not None:
        query = query.filter(PaperReview.version == version)

    reviews = query.all()

    reviews_list = [Review(
        aixiv_id=r.aixiv_id,
        version=r.version,
        review_results=r.review_results,
        create_time=r.create_time,
        reviewer=ReviewerConst.REVIEWERS_TYPE_MAP.get(r.agent_type, ReviewerConst.UNKNOWN_REVIEWER),
    ) for r in reviews]

    return reviews_list
