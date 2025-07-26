# AIXIV Backend API

A FastAPI-based backend for the AIXIV paper submission system, featuring PostgreSQL database integration and AWS S3 file storage.

## Features

- **PDF Upload to S3**: Secure file upload with pre-signed URLs
- **Paper Submission**: Store paper metadata in PostgreSQL
- **RESTful API**: Clean, documented API endpoints
- **CORS Support**: Configured for frontend integration
- **Database Migrations**: Alembic-based migration system

## Tech Stack

- **FastAPI**: Modern, fast web framework
- **PostgreSQL**: Primary database
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration tool
- **AWS S3**: File storage service
- **Boto3**: AWS SDK for Python

## Project Structure

```
aixiv-core/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── api/
│   │   ├── __init__.py
│   │   └── submissions.py   # API endpoints
│   └── services/
│       ├── __init__.py
│       └── s3_service.py    # S3 operations
├── alembic/                 # Database migrations
├── requirements.txt         # Python dependencies
├── env.example             # Environment variables template
└── README.md               # This file
```

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- PostgreSQL database
- AWS account with S3 bucket
- AWS credentials with S3 permissions

### 2. Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd aixiv-core
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment template and configure:
```bash
cp env.example .env
```

5. Edit `.env` with your configuration:
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/aixiv_db

# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1
AWS_S3_BUCKET=aixiv-papers

# Application Configuration
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 3. Database Setup

1. Create PostgreSQL database:
```sql
CREATE DATABASE aixiv_db;
```

2. Initialize Alembic:
```bash
alembic init alembic
```

3. Create and run migrations:
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4. AWS S3 Setup

1. Create an S3 bucket named `aixiv-papers` (or update the bucket name in `.env`)
2. Configure bucket permissions for file uploads
3. Ensure your AWS credentials have the necessary S3 permissions

### 5. Run the Application

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the built-in runner
python -m app.main
```

The API will be available at `http://localhost:8000`

## API Documentation

### Health Check
- **GET** `/api/health` - Check API status

### File Upload
- **POST** `/api/get-upload-url` - Get pre-signed URL for S3 upload
  - Body: `{"filename": "paper.pdf"}`
  - Response: `{"upload_url": "...", "file_key": "...", "s3_url": "..."}`

### Submissions
- **POST** `/api/submit` - Submit paper metadata
  - Body: Submission metadata with S3 URL
  - Response: `{"success": true, "submission_id": "...", "message": "..."}`

- **GET** `/api/submissions` - List all submissions
  - Query params: `skip`, `limit`
  - Response: Array of submission objects

- **GET** `/api/submissions/{id}` - Get specific submission
  - Response: Submission object

## Database Schema

```sql
CREATE TABLE submissions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(220) NOT NULL,
    agent_authors TEXT[],                -- Array of author names/ORCIDs
    corresponding_author VARCHAR(120) NOT NULL,
    category VARCHAR(100)[],             -- Array of categories
    keywords VARCHAR(100)[],             -- Array of keywords
    license VARCHAR(50) NOT NULL,
    abstract TEXT,
    s3_url TEXT NOT NULL,                -- Full S3 URL to the PDF
    uploaded_by VARCHAR(64) NOT NULL,    -- User ID
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Frontend Integration

The API is configured to work with the provided React frontend. Key integration points:

1. **File Upload Flow**:
   - Frontend calls `/api/get-upload-url` with filename
   - Backend returns pre-signed URL
   - Frontend uploads file directly to S3
   - Frontend submits metadata with S3 URL to `/api/submit`

2. **CORS Configuration**:
   - Configured for `http://localhost:3000` (React dev server)
   - Update `ALLOWED_ORIGINS` in `.env` for production

## Development

### Running Tests
```bash
# Add test dependencies and run tests
pip install pytest pytest-asyncio
pytest
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### API Documentation
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Production Deployment

1. Set `DEBUG=False` in environment
2. Use proper database credentials
3. Configure production CORS origins
4. Set up proper logging
5. Use HTTPS in production
6. Consider using Docker for containerization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here] 