import pytest
from datetime import date, datetime
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


@pytest.fixture
def sample_car():
    """Create a sample car."""
    car = Car(
        brand="Toyota",
        model="Camry",
        year=2023,
        color="Blue",
        daily_price=35000.0,
        vin="1HGBH41JXMN109186", 
        status=CarStatus.AVAILABLE,
        dealer_id=1
    )
    return car_repo.create(car)


def test_create_car(client):
    """Test creating a new car."""
    car_data = {
        "brand": "Honda",
        "model": "Accord",
        "year": 2024,
        "color": "Red",
        "daily_price": 32000.0,
        "vin": "2HGBH41JXMN109187",
        "status": "available",
        "dealer_id": 1
    }
    response = client.post("/api/v1/cars", json=car_data)
    assert response.status_code == 201
    data = response.json()
    assert data["brand"] == "Honda"
    assert data["model"] == "Accord"
    assert data["year"] == 2024
    assert data["id"] is not None


def test_create_car_duplicate_vin(client):
    """Test creating a car with duplicate VIN."""
    car_data = {
        "brand": "Toyota",
        "model": "Camry",
        "year": 2023,
        "color": "Blue",
        "daily_price": 35000.0,
        "vin": "1HGBH41JXMN109186", 
        "status": "available",
        "dealer_id": 1
    }
    client.post("/api/v1/cars", json=car_data)
    
    # Try to create another car with same VIN
    response = client.post("/api/v1/cars", json=car_data)
    response.json()["detail"] == "Car with this VIN already exists"
    assert response.status_code == 400


def test_get_cars(client, sample_car):
    """Test getting all cars."""
    response = client.get("/api/v1/cars")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["brand"] == "Toyota"


def test_get_car_by_id(client, sample_car):
    """Test getting a specific car."""
    response = client.get(f"/api/v1/cars/{sample_car.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["brand"] == "Toyota"
    assert data["id"] == sample_car.id


def test_get_car_not_found(client):
    """Test getting a non-existent car."""
    response = client.get("/api/v1/cars/999")
    assert response.status_code == 404


def test_create_car_invalid_dealer_id(client):
    """Test creating a car with non-existent dealer_id."""
    car_data = {
        "brand": "Toyota",
        "model": "Camry",
        "year": 2023,
        "color": "Blue",
        "daily_price": 35000.0,
        "vin": "1HGBH41JXMN109186",
        "dealer_id": 999
    }
    response = client.post("/api/v1/cars", json=car_data)
    assert response.status_code == 404
    assert "Dealer with id 999 not found" in response.json()["detail"]


def test_update_car(client, sample_car):
    """Test updating a car."""
    update_data = {
        "color": "Red",
        "daily_price": 36000.0
    }
    response = client.put(f"/api/v1/cars/{sample_car.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["color"] == "Red"
    assert data["daily_price"] == 36000.0
    assert data["brand"] == "Toyota"  # Unchanged field


def test_update_car_status(client, sample_car):
    """Test updating car status."""
    update_data = {
        "status": "maintenance"
    }
    response = client.put(f"/api/v1/cars/{sample_car.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "maintenance"
    assert data["brand"] == "Toyota"  # Unchanged field


def test_update_car_invalid_dealer_id(client, sample_car):
    """Test updating a car with non-existent dealer_id."""
    update_data = {
        "dealer_id": 999
    }
    response = client.put(f"/api/v1/cars/{sample_car.id}", json=update_data)
    assert response.status_code == 404
    assert "Dealer with id 999 not found" in response.json()["detail"]


def test_create_car_with_status(client):
    """Test creating a car with specific status."""
    car_data = {
        "brand": "Ford",
        "model": "Focus",
        "year": 2022,
        "color": "Black",
        "daily_price": 25000.0,
        "vin": "3HGBH41JXMN109188",
        "status": "maintenance",
        "dealer_id": 1
    }
    response = client.post("/api/v1/cars", json=car_data)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "maintenance"


def test_delete_car(client, sample_car):
    """Test deleting a car."""
    response = client.delete(f"/api/v1/cars/{sample_car.id}")
    assert response.status_code == 204
    
    # Verify car is deleted
    response = client.get(f"/api/v1/cars/{sample_car.id}")
    assert response.status_code == 404


def test_get_cars_without_date_range_returns_all(client, sample_car):
    """Test that getting cars without date range parameters returns all cars."""
    # Create a car in maintenance
    maintenance_car = Car(
        brand="Ford",
        model="Focus",
        year=2022,
        color="Black",
        daily_price=25000.0,
        vin="3HGBH41JXMN109188",
        status=CarStatus.MAINTENANCE,
        dealer_id=1
    )
    maintenance_car = car_repo.create(maintenance_car)
    
    # Get all cars without date range filter
    response = client.get("/api/v1/cars")
    assert response.status_code == 200
    data = response.json()
    # Should return all cars regardless of status
    assert len(data) == 2

