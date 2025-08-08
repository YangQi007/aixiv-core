from sqlalchemy.orm import Session
from app.models import Submission, UserProfile
from app.schemas import SubmissionCreate
from typing import List, Optional, Dict

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