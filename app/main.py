from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.submissions import router as submissions_router
from app.api.agent_review import router as agent_review_router
from app.database import engine
from app.models import Base

# Create database tables only if not in test environment
import os
if not os.getenv("TESTING"):
    Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="AIXIV Backend API",
    description="Backend API for AIXIV paper submission system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(submissions_router)
app.include_router(agent_review_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AIXIV Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    ) 