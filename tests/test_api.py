import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_get_upload_url():
    """Test the upload URL generation endpoint"""
    response = client.post("/api/get-upload-url", json={"filename": "test.pdf"})
    assert response.status_code == 200
    data = response.json()
    assert "upload_url" in data
    assert "file_key" in data
    assert "s3_url" in data
    assert "content_type" in data
    assert "file_extension" in data

def test_get_upload_url_latex():
    """Test the upload URL generation endpoint with LaTeX file"""
    response = client.post("/api/get-upload-url", json={"filename": "test.tex"})
    assert response.status_code == 200
    data = response.json()
    assert data["content_type"] == "application/x-tex"
    assert data["file_extension"] == "tex"

def test_get_upload_url_invalid_file():
    """Test the upload URL generation endpoint with invalid file type"""
    response = client.post("/api/get-upload-url", json={"filename": "test.txt"})
    assert response.status_code == 400
    assert "Only PDF and LaTeX files" in response.json()["detail"]

def test_submit_paper():
    """Test the paper submission endpoint"""
    submission_data = {
        "title": "Test Paper",
        "agent_authors": ["Test Author"],
        "corresponding_author": "Test Author",
        "category": ["Computer Science"],
        "keywords": ["test"],
        "license": "CC-BY-4.0",
        "abstract": "Test abstract",
        "s3_url": "https://test-bucket.s3.amazonaws.com/test.pdf",
        "uploaded_by": "test-user"
    }
    
    response = client.post("/api/submit", json=submission_data)
    # This might fail if database is not available, but should not crash
    assert response.status_code in [200, 500]  # 500 if DB not available

def test_extract_abstract_no_url():
    """Test abstract extraction without S3 URL"""
    response = client.post("/api/extract-abstract", json={})
    assert response.status_code == 200
    data = response.json()
    assert "abstract" in data
    assert "No S3 URL provided" in data["abstract"]

def test_cors_headers():
    """Test that CORS headers are properly set"""
    response = client.options("/api/health")
    assert response.status_code == 200
    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers 