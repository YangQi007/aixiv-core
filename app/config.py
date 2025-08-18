import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database - support both old and new field names
    database_url: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/aixiv_db")
    
    # Legacy database fields (for backward compatibility)
    db_username: str = os.getenv("DB_USERNAME", "username")
    db_password: str = os.getenv("DB_PASSWORD", "password")
    db_name: str = os.getenv("DB_NAME", "aixiv_db")
    
    # AWS Configuration
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    aws_s3_bucket: str = os.getenv("AWS_S3_BUCKET", "aixiv-papers")
    
    # Application
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    auth_token: str = os.getenv("AUTH_TOKEN", "your-auth-token-here")
    
    # CORS Configuration - handle both env var and default
    @property
    def allowed_origins(self) -> List[str]:
        # Check if ALLOWED_ORIGINS is set in environment
        env_origins = os.getenv("ALLOWED_ORIGINS")
        if env_origins:
            # Parse comma-separated string from environment
            return [origin.strip() for origin in env_origins.split(",")]
        
        # Default origins (simplified - only essential ones)
        return [
            "https://aixiv.co",
            "https://www.aixiv.co",
            "http://localhost:3000",  # for local development
        ]
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields instead of raising errors

settings = Settings() 