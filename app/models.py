from sqlalchemy import Column, Integer, String, Text, ARRAY, DateTime, BigInteger, Index, text,SmallInteger, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base

class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(220), nullable=False)
    agent_authors = Column(ARRAY(Text), nullable=False)
    corresponding_author = Column(String(120), nullable=False)
    category = Column(ARRAY(String(100)), nullable=False)
    keywords = Column(ARRAY(String(100)), nullable=False)
    license = Column(String(50), nullable=False)
    abstract = Column(Text)
    s3_url = Column(Text, nullable=False)
    uploaded_by = Column(String(64), nullable=False)  # Assuming this references a users table
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    title = Column(String(255))
    affiliation = Column(String(500))
    location = Column(String(255))
    bio = Column(Text)
    email = Column(String(255))
    website = Column(String(500))
    github_url = Column(String(500))
    twitter_url = Column(String(500))
    linkedin_url = Column(String(500))
    avatar_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class PaperReview(Base):
    __tablename__ = "paper_review"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    aixiv_id = Column(String(128), nullable=False)
    version = Column(String(45), nullable=False)
    review_results = Column(JSONB, nullable=False)
    agent_type = Column(SmallInteger, nullable=False, server_default=text("1"))
    doc_type = Column(SmallInteger, nullable=False, server_default=text("1"))
    create_time = Column(
        TIMESTAMP, nullable=False, server_default=func.now()
    )
    like_count = Column(Integer, nullable=False, server_default=text("0"))

    __table_args__ = (
        Index("idx_paper_review_aixiv_id_create_time", "aixiv_id", "create_time"),
    )