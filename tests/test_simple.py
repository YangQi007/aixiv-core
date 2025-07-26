import pytest
import os

def test_environment_variable():
    """Test that TESTING environment variable is set"""
    assert os.getenv("TESTING") == "true"

def test_import_app():
    """Test that we can import the app without errors"""
    try:
        from app.main import app
        assert app is not None
        print("✅ App imported successfully")
    except Exception as e:
        pytest.fail(f"Failed to import app: {e}")

def test_import_config():
    """Test that we can import the config without errors"""
    try:
        from app.config import settings
        assert settings is not None
        print("✅ Config imported successfully")
    except Exception as e:
        pytest.fail(f"Failed to import config: {e}")

def test_import_models():
    """Test that we can import the models without errors"""
    try:
        from app.models import Submission
        assert Submission is not None
        print("✅ Models imported successfully")
    except Exception as e:
        pytest.fail(f"Failed to import models: {e}")

def test_import_schemas():
    """Test that we can import the schemas without errors"""
    try:
        from app.schemas import SubmissionCreate
        assert SubmissionCreate is not None
        print("✅ Schemas imported successfully")
    except Exception as e:
        pytest.fail(f"Failed to import schemas: {e}") 