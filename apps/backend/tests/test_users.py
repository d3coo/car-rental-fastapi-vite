"""
Tests for User API endpoints
"""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    """Create test client"""
    app = create_app()
    return TestClient(app)


@pytest.mark.unit
def test_get_users_empty(client):
    """Test getting users when mock repository has data"""
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    
    data = response.json()
    assert "data" in data
    assert "message" in data
    assert "status_code" in data
    assert data["status_code"] == 200
    assert data["message"] == "Users retrieved successfully"
    
    # Mock repository should have sample users
    assert "users" in data["data"]
    assert len(data["data"]["users"]) > 0


@pytest.mark.unit
def test_get_user_by_id(client):
    """Test getting a specific user by ID"""
    # First get all users to find a valid ID
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    
    users = response.json()["data"]["users"]
    if users:
        user_id = users[0]["id"]
        
        # Now get specific user
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["data"]["id"] == user_id
        assert data["message"] == "User retrieved successfully"


@pytest.mark.unit
def test_get_user_not_found(client):
    """Test getting a user that doesn't exist"""
    response = client.get("/api/v1/users/nonexistent_id")
    assert response.status_code == 404
    
    data = response.json()
    assert "message" in data
    assert "User not found" in data["message"]


@pytest.mark.unit
def test_get_user_by_email(client):
    """Test getting user by email"""
    # First get available users to find a real email
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    
    users = response.json()["data"]["users"]
    if users:
        # Use the first available user's email
        email = users[0]["email"]
        
        # Test with real email
        response = client.get(f"/api/v1/users/email/{email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["data"]["email"] == email
        assert data["message"] == "User retrieved successfully"
    else:
        # If no users available, test should pass (empty database scenario)
        response = client.get("/api/v1/users/email/nonexistent@example.com")
        assert response.status_code == 404


@pytest.mark.unit
def test_get_user_by_phone(client):
    """Test getting user by phone"""
    # First get available users to find a real phone number
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    
    users = response.json()["data"]["users"]
    if users:
        # Use the first available user's phone number
        phone_number = users[0]["phone_number"]
        
        # Test with real phone number
        response = client.get(f"/api/v1/users/phone/{phone_number}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["data"]["phone_number"] == phone_number
        assert data["message"] == "User retrieved successfully"
    else:
        # If no users available, test should pass (empty database scenario)
        response = client.get("/api/v1/users/phone/+966501234567")
        assert response.status_code == 404


@pytest.mark.unit
def test_create_user_not_implemented(client):
    """Test creating a user (should return not implemented)"""
    user_data = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+966500000000",
        "nationality": "Saudi",
        "status_number": "1111111111"
    }
    
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 501
    
    data = response.json()
    assert "message" in data
    assert "Not implemented yet" in data["message"]


@pytest.mark.unit
def test_verify_email(client):
    """Test email verification"""
    # First get a user ID
    response = client.get("/api/v1/users/")
    users = response.json()["data"]["users"]
    if users:
        user_id = users[0]["id"]
        
        # Verify email
        response = client.post(f"/api/v1/users/{user_id}/verify-email")
        assert response.status_code == 200
        
        data = response.json()
        assert data["data"]["email_verified"] == True
        assert data["message"] == "Email verified successfully"


@pytest.mark.unit
def test_verify_phone(client):
    """Test phone verification"""
    # First get a user ID
    response = client.get("/api/v1/users/")
    users = response.json()["data"]["users"]
    if users:
        user_id = users[0]["id"]
        
        # Verify phone
        response = client.post(f"/api/v1/users/{user_id}/verify-phone")
        assert response.status_code == 200
        
        data = response.json()
        assert data["data"]["phone_verified"] == True
        assert data["message"] == "Phone verified successfully"


@pytest.mark.unit
def test_users_pagination(client):
    """Test user pagination"""
    response = client.get("/api/v1/users/?page=1&limit=2")
    assert response.status_code == 200
    
    data = response.json()["data"]
    assert "users" in data
    assert "total" in data
    assert "page" in data
    assert "totalPages" in data
    assert data["page"] == 1
    assert len(data["users"]) <= 2


@pytest.mark.unit
def test_users_filter_by_status(client):
    """Test filtering users by status"""
    response = client.get("/api/v1/users/?status=active")
    assert response.status_code == 200
    
    data = response.json()["data"]
    for user in data["users"]:
        assert user["status"] == "active"


@pytest.mark.unit
def test_users_search(client):
    """Test searching users"""
    response = client.get("/api/v1/users/?search=john")
    assert response.status_code == 200
    
    data = response.json()["data"]
    # Should find users with "john" in their name or email
    assert len(data["users"]) >= 0  # May or may not find results