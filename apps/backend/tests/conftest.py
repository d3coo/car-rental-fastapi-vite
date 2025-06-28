"""
Pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from app.main import create_app


@pytest.fixture(scope="session")
def app():
    """Create FastAPI app for testing"""
    return create_app()


@pytest.fixture(scope="session") 
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture(scope="function")
def mock_firebase():
    """Mock Firebase dependencies for testing"""
    # This would normally mock Firebase services
    # For now, we'll use the existing mock repositories
    pass