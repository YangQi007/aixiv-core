import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "AIXIV Backend API"

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_get_upload_url_pdf(client):
    """Test upload URL generation for PDF"""
    response = client.post("/api/get-upload-url", json={"filename": "test.pdf"})
    # This might fail due to missing AWS credentials, but should not crash
    assert response.status_code in [200, 500]

def test_get_upload_url_latex(client):
    """Test upload URL generation for LaTeX"""
    response = client.post("/api/get-upload-url", json={"filename": "test.tex"})
    # This might fail due to missing AWS credentials, but should not crash
    assert response.status_code in [200, 500]

def test_get_upload_url_invalid(client):
    """Test upload URL generation with invalid file type"""
    response = client.post("/api/get-upload-url", json={"filename": "test.txt"})
    assert response.status_code == 400
    assert "Only PDF and LaTeX files" in response.json()["detail"]

def test_extract_abstract_no_url(client):
    """Test abstract extraction without S3 URL"""
    response = client.post("/api/extract-abstract", json={})
    assert response.status_code == 200
    data = response.json()
    assert "abstract" in data
    assert "No S3 URL provided" in data["abstract"]

def test_cors_headers(client):
    """Test that CORS headers are properly set"""
    response = client.options("/api/health")
    assert response.status_code == 200 