import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/aixiv_db")
    
    # AWS Configuration
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    aws_s3_bucket: str = os.getenv("AWS_S3_BUCKET", "aixiv-papers")
    
    # Application
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    auth_token: str = os.getenv("AUTH_TOKEN", "your-auth-token-here")
    
    # CORS Configuration
    allowed_origins: List[str] = [
        "https://aixiv.co",
        "https://www.aixiv.co",
        "http://localhost:3000",  # for local development
        "http://localhost:3001",  # alternative port
        "http://127.0.0.1:3000",  # alternative localhost
        "http://127.0.0.1:3001",  # alternative localhost and port
    ]
    
    class Config:
        env_file = ".env"

settings = Settings() 