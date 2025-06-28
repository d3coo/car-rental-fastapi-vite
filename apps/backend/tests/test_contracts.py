"""
Test contracts API endpoints
"""
import pytest
from fastapi import status


@pytest.mark.unit
def test_get_contracts_empty(client):
    """Test getting contracts returns empty list initially"""
    response = client.get("/api/v1/contracts/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == []


@pytest.mark.unit
def test_get_contract_not_found(client):
    """Test getting non-existent contract returns 404"""
    response = client.get("/api/v1/contracts/nonexistent-id")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["message"] == "Contract not found"


@pytest.mark.unit
def test_create_contract_not_implemented(client):
    """Test creating contract returns not implemented"""
    contract_data = {
        "user_id": "user123",
        "car_id": "car123", 
        "start_date": "2025-07-01",
        "end_date": "2025-07-07"
    }
    
    response = client.post("/api/v1/contracts/", json=contract_data)
    
    assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED
    data = response.json()
    assert data["message"] == "Not implemented yet"