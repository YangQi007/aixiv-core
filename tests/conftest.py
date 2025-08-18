"""
Pytest configuration and common fixtures for AIXIV tests
"""
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest

@pytest.fixture
def client():
    """Test client fixture for all tests"""
    # Import here to avoid import issues
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)
    except Exception as e:
        # If TestClient fails, try alternative approach
        import httpx
        from app.main import app
        return httpx.Client(app=app, base_url="http://test")

@pytest.fixture
def sample_submission_data():
    """Sample submission data for testing"""
    return {
        "title": "Test Paper",
        "agent_authors": ["Test Author"],
        "corresponding_author": "Test Author",
        "category": ["Computer Science"],
        "keywords": ["test"],
        "license": "CC-BY-4.0",
        "abstract": "Test abstract",
        "s3_url": "https://test-bucket.s3.amazonaws.com/test.pdf",
        "uploaded_by": "test-user",
        # Required field
        "doc_type": "paper",
        # Optional field
        "doi": "10.1000/test.2024.001"
        # Note: aixiv_id, version, and status are now server-generated
    }

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test"""
    # Set testing environment
    os.environ["TESTING"] = "true"
    yield
    # Cleanup after each test
    pass

@pytest.fixture
def mock_db():
    """Mock database session for tests"""
    return Mock() 