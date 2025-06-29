"""
Pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.infrastructure.dependencies import get_contract_repository, get_car_repository, get_user_repository, get_dependency_container
from app.infrastructure.persistence.mock_contract_repository import MockContractRepository
from app.infrastructure.persistence.mock_car_repository import MockCarRepository
from app.infrastructure.persistence.mock_user_repository import MockUserRepository


@pytest.fixture(scope="session")
def app():
    """Create FastAPI app for testing with mock dependencies"""
    # Clear the dependency container cache to avoid using existing Firebase instances
    get_dependency_container.cache_clear()
    
    app = create_app()
    
    # Override dependencies to use mock repositories for testing
    def override_contract_repo():
        return MockContractRepository()
    
    def override_car_repo():
        return MockCarRepository()
    
    def override_user_repo():
        return MockUserRepository()
    
    app.dependency_overrides[get_contract_repository] = override_contract_repo
    app.dependency_overrides[get_car_repository] = override_car_repo
    app.dependency_overrides[get_user_repository] = override_user_repo
    
    return app


@pytest.fixture(scope="session") 
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture(scope="function")
def mock_firebase():
    """Mock Firebase dependencies for testing"""
    # Dependencies are already overridden in the app fixture
    pass