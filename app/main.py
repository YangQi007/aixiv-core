from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.config import settings
from app.api.submissions import router as submissions_router
from app.api.profiles import router as profiles_router
from app.api.agent_review import router as agent_review_router
from app.database import engine
from app.models import Base
import os
import json

# Create database tables only if not in test environment
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

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(submissions_router)
app.include_router(agent_review_router)
app.include_router(profiles_router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AIXIV Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon - tries .ico first, then .svg, then returns 204"""
    favicon_ico = "static/favicon.ico"
    favicon_svg = "static/favicon.svg"

    if os.path.exists(favicon_ico):
        return FileResponse(favicon_ico, media_type="image/x-icon")
    elif os.path.exists(favicon_svg):
        return FileResponse(favicon_svg, media_type="image/svg+xml")

    # Return 204 No Content if no favicon exists
    from fastapi import Response
    return Response(status_code=204)

@app.get("/manifest.json")
async def manifest():
    """Serve manifest.json"""
    manifest_path = "static/manifest.json"
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            return JSONResponse(content=json.load(f))
    # Return default manifest if file doesn't exist
    return JSONResponse(content={
        "name": "AIXIV",
        "short_name": "AIXIV",
        "description": "AI Agent Research Paper Repository",
        "start_url": "/",
        "display": "standalone",
        "theme_color": "#3B82F6",
        "background_color": "#ffffff"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    ) 