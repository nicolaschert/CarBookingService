import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app, car_repo, booking_repo, dealer_repo
from app.domain.models import Car, Booking, CarStatus, Dealer


@pytest.fixture(autouse=True)
def clear_database():
    """Clear databases before each test."""
    car_repo.db.clear()
    booking_repo.db.clear()
    dealer_repo.db.clear()
    # Ensure initial dealer exists for tests
    if not dealer_repo.get_all():
        initial_dealer = Dealer(name="Oscar Mobility Main", location="New York, NY")
        dealer_repo.create(initial_dealer)
    yield
    car_repo.db.clear()
    booking_repo.db.clear()
    dealer_repo.db.clear()


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_car_deletion_with_bookings(client):
    """Test that a car with bookings cannot be deleted."""
    # Create a car
    car_data = {
        "brand": "Toyota",
        "model": "Camry",
        "year": 2023,
        "color": "Blue",
        "daily_price": 35000.0,
        "vin": "1HGBH41JXMN109186",
        "dealer_id": 1
    }
    car_response = client.post("/api/v1/cars", json=car_data)
    car_id = car_response.json()["id"]
    
    # Create a booking for the car
    booking_data = {
        "car_id": car_id,
        "customer_name": "John D",
        "customer_email": "john@example.com",
        "start_datetime": "2024-01-15T10:00:00",
        "end_datetime": "2024-01-20T14:00:00"
    }
    client.post("/api/v1/bookings", json=booking_data)
    
    # Try to delete the car
    response = client.delete(f"/api/v1/cars/{car_id}")
    assert response.status_code == 400
    
    # Verify car still exists
    response = client.get(f"/api/v1/cars/{car_id}")
    assert response.status_code == 200


def test_booking_workflow(client):
    """Test complete booking workflow."""
    # Create a car
    car_data = {
        "brand": "Honda",
        "model": "Accord",
        "year": 2024,
        "color": "Red",
        "daily_price": 32000.0,
        "vin": "2HGBH41JXMN109187",
        "dealer_id": 1
    }
    car_response = client.post("/api/v1/cars", json=car_data)
    car_id = car_response.json()["id"]
    
    # Create a booking
    booking_data = {
        "car_id": car_id,
        "customer_name": "Alice J",
        "customer_email": "alice@example.com",
        "start_datetime": "2024-03-01T10:00:00",
        "end_datetime": "2024-03-10T14:00:00"
    }
    booking_response = client.post("/api/v1/bookings", json=booking_data)
    assert booking_response.status_code == 201
    booking_id = booking_response.json()["id"]
    
    # Verify booking exists
    response = client.get(f"/api/v1/bookings/{booking_id}")
    assert response.status_code == 200
    
    # Get bookings for the car
    response = client.get(f"/api/v1/bookings?car_id={car_id}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    
    # Try to create overlapping booking (should fail)
    overlapping_booking = {
        "car_id": car_id,
        "customer_name": "Bob S",
        "customer_email": "bob@example.com",
        "start_datetime": "2024-03-05T10:00:00",
        "end_datetime": "2024-03-15T14:00:00"
    }
    response = client.post("/api/v1/bookings", json=overlapping_booking)
    assert response.status_code == 400
    
    # Create non-overlapping booking (should succeed)
    non_overlapping_booking = {
        "car_id": car_id,
        "customer_name": "Charlie B",
        "customer_email": "charlie@example.com",
        "start_datetime": "2024-03-11T10:00:00",
        "end_datetime": "2024-03-15T14:00:00"
    }
    response = client.post("/api/v1/bookings", json=non_overlapping_booking)
    assert response.status_code == 201
    
    # Get all bookings for the car
    response = client.get(f"/api/v1/bookings?car_id={car_id}")
    assert response.status_code == 200
    assert len(response.json()) == 2
    
    # Cancel first booking
    response = client.delete(f"/api/v1/bookings/{booking_id}")
    assert response.status_code == 204
    
    # Verify booking is deleted
    response = client.get(f"/api/v1/bookings/{booking_id}")
    assert response.status_code == 404

