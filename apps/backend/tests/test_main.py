"""
Test main application endpoints
"""
import pytest
from fastapi import status


@pytest.mark.unit
def test_root_endpoint(client):
    """Test root endpoint returns correct response"""
    response = client.get("/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Car Rental System API v3.0"
    assert data["status"] == "running"
    assert data["architecture"] == "FastAPI + Domain-Driven Design"
    assert "timestamp" in data


@pytest.mark.unit  
def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "3.0.0"
    assert data["architecture"] == "FastAPI + DDD"
    assert "timestamp" in data


@pytest.mark.unit
def test_nonexistent_endpoint(client):
    """Test 404 handling"""
    response = client.get("/nonexistent")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["error"] == "Not found"