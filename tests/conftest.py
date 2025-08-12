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
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Test client fixture for all tests"""
    return TestClient(app)

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
        "uploaded_by": "test-user"
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