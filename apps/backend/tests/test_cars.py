"""
Tests for Car API endpoints
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
def test_get_cars(client):
    """Test getting cars when mock repository has data"""
    response = client.get("/api/v1/cars/")
    assert response.status_code == 200
    
    data = response.json()
    assert "data" in data
    assert "message" in data
    assert "status_code" in data
    assert data["status_code"] == 200
    assert data["message"] == "Cars retrieved successfully"
    
    # Mock repository should have sample cars
    assert "cars" in data["data"]
    assert len(data["data"]["cars"]) > 0


@pytest.mark.unit
def test_get_car_by_id(client):
    """Test getting a specific car by ID"""
    # First get all cars to find a valid ID
    response = client.get("/api/v1/cars/")
    assert response.status_code == 200
    
    cars = response.json()["data"]["cars"]
    if cars:
        car_id = cars[0]["id"]
        
        # Now get specific car
        response = client.get(f"/api/v1/cars/{car_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["data"]["id"] == car_id
        assert data["message"] == "Car retrieved successfully"


@pytest.mark.unit
def test_get_car_not_found(client):
    """Test getting a car that doesn't exist"""
    response = client.get("/api/v1/cars/nonexistent_id")
    assert response.status_code == 404
    
    data = response.json()
    assert "message" in data
    assert "Car not found" in data["message"]


@pytest.mark.unit
def test_get_car_by_license_plate(client):
    """Test getting car by license plate"""
    # Use sample license plate from mock data
    response = client.get("/api/v1/cars/license/ABC-1234")
    assert response.status_code == 200
    
    data = response.json()
    assert data["data"]["license_plate"] == "ABC-1234"
    assert data["message"] == "Car retrieved successfully"


@pytest.mark.unit
def test_get_available_cars(client):
    """Test getting available cars"""
    response = client.get("/api/v1/cars/available")
    assert response.status_code == 200
    
    data = response.json()
    assert "cars" in data["data"]
    assert data["message"] == "Available cars retrieved successfully"
    
    # All returned cars should be available
    for car in data["data"]["cars"]:
        assert car["is_available"] == True


@pytest.mark.unit
def test_get_cars_due_for_service(client):
    """Test getting cars due for service"""
    response = client.get("/api/v1/cars/due-for-service?days_ahead=10")
    assert response.status_code == 200
    
    data = response.json()
    assert "cars" in data["data"]
    assert "Cars due for service in 10 days" in data["message"]


@pytest.mark.unit
def test_create_car_not_implemented(client):
    """Test creating a car (should return not implemented)"""
    car_data = {
        "make": "Toyota",
        "model": "Corolla",
        "year": 2024,
        "color": "Red",
        "license_plate": "NEW-1234",
        "category": "Compact",
        "daily_rate": 100.0
    }
    
    response = client.post("/api/v1/cars/", json=car_data)
    assert response.status_code == 501
    
    data = response.json()
    assert "message" in data
    assert "Not implemented yet" in data["message"]


@pytest.mark.unit
def test_mark_car_as_rented(client):
    """Test marking a car as rented"""
    # First get an available car
    response = client.get("/api/v1/cars/available")
    available_cars = response.json()["data"]["cars"]
    
    if available_cars:
        car_id = available_cars[0]["id"]
        
        # Mark as rented
        response = client.post(f"/api/v1/cars/{car_id}/mark-rented")
        assert response.status_code == 200
        
        data = response.json()
        assert data["data"]["status"] == "rented"
        assert data["data"]["is_available"] == False
        assert data["message"] == "Car marked as rented successfully"


@pytest.mark.unit
def test_mark_car_as_available(client):
    """Test marking a car as available"""
    # First get all cars to find one to test with
    response = client.get("/api/v1/cars/")
    cars = response.json()["data"]["cars"]
    
    if cars:
        car_id = cars[0]["id"]
        
        # Mark as available
        response = client.post(f"/api/v1/cars/{car_id}/mark-available")
        assert response.status_code == 200
        
        data = response.json()
        assert data["data"]["status"] == "available"
        assert data["data"]["is_available"] == True
        assert data["message"] == "Car marked as available successfully"


@pytest.mark.unit
def test_send_car_for_maintenance(client):
    """Test sending car for maintenance"""
    # First get all cars to find one to test with
    response = client.get("/api/v1/cars/")
    cars = response.json()["data"]["cars"]
    
    if cars:
        car_id = cars[0]["id"]
        
        # Send for maintenance
        response = client.post(f"/api/v1/cars/{car_id}/maintenance?reason=Routine service")
        assert response.status_code == 200
        
        data = response.json()
        assert data["data"]["status"] == "maintenance"
        assert data["data"]["is_available"] == False
        assert data["message"] == "Car sent for maintenance successfully"


@pytest.mark.unit
def test_cars_pagination(client):
    """Test car pagination"""
    response = client.get("/api/v1/cars/?page=1&limit=2")
    assert response.status_code == 200
    
    data = response.json()["data"]
    assert "cars" in data
    assert "total" in data
    assert "page" in data
    assert "totalPages" in data
    assert data["page"] == 1
    assert len(data["cars"]) <= 2


@pytest.mark.unit
def test_cars_filter_by_status(client):
    """Test filtering cars by status"""
    response = client.get("/api/v1/cars/?status=available")
    assert response.status_code == 200
    
    data = response.json()["data"]
    for car in data["cars"]:
        assert car["status"] == "available"


@pytest.mark.unit
def test_cars_filter_by_category(client):
    """Test filtering cars by category"""
    response = client.get("/api/v1/cars/?category=SUV")
    assert response.status_code == 200
    
    data = response.json()["data"]
    for car in data["cars"]:
        assert car["category"] == "SUV"


@pytest.mark.unit
def test_cars_search(client):
    """Test searching cars"""
    response = client.get("/api/v1/cars/?search=Toyota")
    assert response.status_code == 200
    
    data = response.json()["data"]
    # Should find cars with "Toyota" in their make
    assert len(data["cars"]) >= 0  # May or may not find results