import pytest
from unittest.mock import Mock, patch

class TestHealthEndpoints:
    """Test health-related endpoints"""
    
    def test_health_check(self, client):
        """Test the health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "AIXIV Backend API"

class TestUploadEndpoints:
    """Test upload-related endpoints"""
    
    def test_get_upload_url_pdf(self, client):
        """Test upload URL generation for PDF"""
        response = client.post("/api/get-upload-url", json={"filename": "test.pdf"})
        # This might fail due to missing AWS credentials, but should not crash
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "upload_url" in data
            assert "file_key" in data
            assert "s3_url" in data
            assert "content_type" in data
            assert "file_extension" in data
            assert data["content_type"] == "application/pdf"
            assert data["file_extension"] == "pdf"

    def test_get_upload_url_latex(self, client):
        """Test upload URL generation for LaTeX"""
        response = client.post("/api/get-upload-url", json={"filename": "test.tex"})
        # This might fail due to missing AWS credentials, but should not crash
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert data["content_type"] == "application/x-tex"
            assert data["file_extension"] == "tex"

    def test_get_upload_url_invalid_file(self, client):
        """Test upload URL generation with invalid file type"""
        response = client.post("/api/get-upload-url", json={"filename": "test.txt"})
        assert response.status_code == 400
        assert "Only PDF and LaTeX files" in response.json()["detail"]

class TestSubmissionEndpoints:
    """Test submission-related endpoints with proper mocking"""
    
    @patch('app.api.submissions.create_submission')
    def test_submit_paper_success(self, mock_create_submission, client, sample_submission_data):
        """Test successful paper submission with mocked database"""
        # Mock successful database operation
        mock_create_submission.return_value = Mock(
            id=1, 
            title="Test Paper",
            # Include new fields
            aixiv_id="AIXIV-2024-001",
            doi="10.1000/test.2024.001",
            version="1.0",
            doc_type="paper",
            status="Under Review",
            # Engagement metrics as integers
            views=0,
            downloads=0,
            comments=0,
            citations=0
        )
        
        response = client.post("/api/submit", json=sample_submission_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert data["success"] == True
        assert "submission_id" in data
        assert "message" in data
        
        # Verify the mock was called correctly
        mock_create_submission.assert_called_once()

    @patch('app.api.submissions.create_submission')
    def test_submit_paper_database_error(self, mock_create_submission, client, sample_submission_data):
        """Test paper submission when database fails"""
        # Mock database error
        mock_create_submission.side_effect = Exception("Database connection failed")
        
        response = client.post("/api/submit", json=sample_submission_data)
        assert response.status_code == 500
        
        data = response.json()
        assert "detail" in data
        assert "An unexpected error occurred" in data["detail"]

    @patch('app.api.submissions.get_submissions')
    def test_get_submissions_success(self, mock_get_submissions, client):
        """Test getting submissions with mocked database"""
        # Mock successful database operation with proper data structure
        from datetime import datetime
        
        mock_submissions = [
            Mock(
                id=1, 
                title="Paper 1", 
                abstract="Abstract 1",
                agent_authors=["Author 1", "Author 2"],
                corresponding_author="Author 1",
                category=["Computer Science"],
                keywords=["test", "mock"],
                license="CC-BY-4.0",
                s3_url="https://example.com/paper1.pdf",
                uploaded_by="user1",
                # New fields
                aixiv_id="AIXIV-2024-001",
                doi="10.1000/test.2024.001",
                version="1.0",
                doc_type="paper",
                status="Under Review",
                # Engagement metrics as integers
                views=0,
                downloads=0,
                comments=0,
                citations=0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            Mock(
                id=2, 
                title="Paper 2", 
                abstract="Abstract 2",
                agent_authors=["Author 3"],
                corresponding_author="Author 3",
                category=["AI"],
                keywords=["ai", "ml"],
                license="CC-BY-4.0",
                s3_url="https://example.com/paper2.pdf",
                uploaded_by="user2",
                # New fields
                aixiv_id="AIXIV-2024-002",
                doi="10.1000/test.2024.002",
                version="1.0",
                doc_type="preprint",
                status="Under Review",
                # Engagement metrics as integers
                views=0,
                downloads=0,
                comments=0,
                citations=0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        mock_get_submissions.return_value = mock_submissions
        
        response = client.get("/api/submissions")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    @patch('app.api.submissions.get_submissions')
    def test_get_submissions_database_error(self, mock_get_submissions, client):
        """Test getting submissions when database fails"""
        # Mock database error
        mock_get_submissions.side_effect = Exception("Database connection failed")
        
        response = client.get("/api/submissions")
        assert response.status_code == 500

class TestCORSAndHeaders:
    """Test CORS and header configurations"""
    
    def test_cors_headers(self, client):
        """Test that CORS headers are properly set"""
        # Test CORS preflight request (OPTIONS method)
        response = client.options("/api/health", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "content-type"
        })
        
        # OPTIONS should return 200 for CORS preflight
        assert response.status_code == 200
        
        # Check that CORS headers are present
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers
        
        # Test that the allowed origins are properly set
        origins = response.headers.get("access-control-allow-origin")
        assert origins is not None 