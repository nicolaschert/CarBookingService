import pytest
from datetime import date, datetime, timedelta
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


def test_create_booking(client, sample_car):
    """Test creating a new booking."""
    booking_data = {
        "car_id": sample_car.id,
        "customer_name": "John Doe",
        "customer_email": "john.doe@example.com",
        "start_datetime": "2024-01-15T10:00:00",
        "end_datetime": "2024-01-20T14:00:00"
    }
    response = client.post("/api/v1/bookings", json=booking_data)
    assert response.status_code == 201
    data = response.json()
    assert data["car_id"] == sample_car.id
    assert data["customer_name"] == "John Doe"
    assert data["id"] is not None


def test_create_booking_car_not_found(client):
    """Test creating a booking for non-existent car."""
    booking_data = {
        "car_id": 999,
        "customer_name": "John Doe",
        "customer_email": "john.doe@example.com",
        "start_datetime": "2024-01-15T10:00:00",
        "end_datetime": "2024-01-20T14:00:00"
    }
    response = client.post("/api/v1/bookings", json=booking_data)
    assert response.status_code == 404


def test_create_booking_maintenance_car(client, sample_car):
    """Test creating a booking for car in maintenance."""
    # Mark car as in maintenance
    from app.domain.models import CarStatus
    sample_car.status = CarStatus.MAINTENANCE
    car_repo.update(sample_car.id, sample_car)
    
    booking_data = {
        "car_id": sample_car.id,
        "customer_name": "John Doe",
        "customer_email": "john.doe@example.com",
        "start_datetime": "2024-01-15T10:00:00",
        "end_datetime": "2024-01-20T14:00:00"
    }
    response = client.post("/api/v1/bookings", json=booking_data)
    assert response.status_code == 400
    assert "not available" in response.json()["detail"].lower()


def test_create_booking_conflicting_datetimes(client, sample_car):
    """Test creating a booking with conflicting datetimes."""
    # Create first booking
    booking1 = Booking(
        car_id=sample_car.id,
        customer_name="John Doe",
        customer_email="john.doe@example.com",
        start_datetime=datetime(2024, 1, 15, 10, 0),
        end_datetime=datetime(2024, 1, 20, 14, 0)
    )
    booking_repo.create(booking1)
    
    # Try to create overlapping booking
    booking_data = {
        "car_id": sample_car.id,
        "customer_name": "Jane Smith",
        "customer_email": "jane.smith@example.com",
        "start_datetime": "2024-01-18T10:00:00",
        "end_datetime": "2024-01-25T14:00:00"
    }
    response = client.post("/api/v1/bookings", json=booking_data)
    response.json()["detail"] == "Overlapping booking"
    assert response.status_code == 400


def test_create_booking_invalid_datetimes(client, sample_car):
    """Test creating a booking with end_datetime before start_datetime."""
    booking_data = {
        "car_id": sample_car.id,
        "customer_name": "John Doe",
        "customer_email": "john.doe@example.com",
        "start_datetime": "2024-01-20T10:00:00",
        "end_datetime": "2024-01-15T14:00:00"
    }
    response = client.post("/api/v1/bookings", json=booking_data)
    assert response.status_code == 422  # Validation error


def test_get_bookings(client, sample_car):
    """Test getting all bookings."""
    booking = Booking(
        car_id=sample_car.id,
        customer_name="John Doe",
        customer_email="john.doe@example.com",
        start_datetime=datetime(2024, 1, 15, 10, 0),
        end_datetime=datetime(2024, 1, 20, 14, 0)
    )
    booking_repo.create(booking)
    
    response = client.get("/api/v1/bookings")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_get_bookings_by_car_id(client, sample_car):
    """Test getting bookings filtered by car ID."""
    booking = Booking(
        car_id=sample_car.id,
        customer_name="John Doe",
        customer_email="john.doe@example.com",
        start_datetime=datetime(2024, 1, 15, 10, 0),
        end_datetime=datetime(2024, 1, 20, 14, 0)
    )
    booking_repo.create(booking)
    
    # Create another car and booking
    car2 = Car(
        brand="Honda",
        model="Accord",
        year=2024,
        color="Red",
        daily_price=32000.0,
        vin="2HGBH41JXMN109187",
        status=CarStatus.AVAILABLE,
        dealer_id=1
    )
    car2 = car_repo.create(car2)
    booking2 = Booking(
        car_id=car2.id,
        customer_name="Jane Smith",
        customer_email="jane.smith@example.com",
        start_datetime=datetime(2024, 2, 1, 10, 0),
        end_datetime=datetime(2024, 2, 5, 14, 0)
    )
    booking_repo.create(booking2)
    
    response = client.get(f"/api/v1/bookings?car_id={sample_car.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["car_id"] == sample_car.id


def test_get_bookings_by_start_datetime(client, sample_car):
    """Test getting bookings filtered by start_datetime."""
    # Create bookings at different times
    booking1 = Booking(
        car_id=sample_car.id,
        customer_name="John Doe",
        customer_email="john.doe@example.com",
        start_datetime=datetime(2024, 1, 15, 10, 0),
        end_datetime=datetime(2024, 1, 20, 14, 0)
    )
    booking_repo.create(booking1)
    
    booking2 = Booking(
        car_id=sample_car.id,
        customer_name="Jane Smith",
        customer_email="jane.smith@example.com",
        start_datetime=datetime(2024, 2, 1, 10, 0),
        end_datetime=datetime(2024, 2, 5, 14, 0)
    )
    booking_repo.create(booking2)
    
    # Filter by start_datetime (should return bookings starting on or after this date)
    response = client.get("/api/v1/bookings?start_datetime=2024-02-01T00:00:00")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["customer_name"] == "Jane Smith"


def test_get_bookings_by_end_datetime(client, sample_car):
    """Test getting bookings filtered by end_datetime."""
    # Create bookings at different times
    booking1 = Booking(
        car_id=sample_car.id,
        customer_name="John Doe",
        customer_email="john.doe@example.com",
        start_datetime=datetime(2024, 1, 15, 10, 0),
        end_datetime=datetime(2024, 1, 20, 14, 0)
    )
    booking_repo.create(booking1)
    
    booking2 = Booking(
        car_id=sample_car.id,
        customer_name="Jane Smith",
        customer_email="jane.smith@example.com",
        start_datetime=datetime(2024, 2, 1, 10, 0),
        end_datetime=datetime(2024, 2, 5, 14, 0)
    )
    booking_repo.create(booking2)
    
    # Filter by end_datetime (should return bookings ending on or before this date)
    response = client.get("/api/v1/bookings?end_datetime=2024-01-25T00:00:00")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["customer_name"] == "John Doe"


def test_get_bookings_by_datetime_range(client, sample_car):
    """Test getting bookings filtered by datetime range (overlap)."""
    # Create bookings at different times
    booking1 = Booking(
        car_id=sample_car.id,
        customer_name="John Doe",
        customer_email="john.doe@example.com",
        start_datetime=datetime(2024, 1, 15, 10, 0),
        end_datetime=datetime(2024, 1, 20, 14, 0)
    )
    booking_repo.create(booking1)
    
    booking2 = Booking(
        car_id=sample_car.id,
        customer_name="Jane Smith",
        customer_email="jane.smith@example.com",
        start_datetime=datetime(2024, 2, 1, 10, 0),
        end_datetime=datetime(2024, 2, 5, 14, 0)
    )
    booking_repo.create(booking2)
    
    booking3 = Booking(
        car_id=sample_car.id,
        customer_name="Bob Wilson",
        customer_email="bob.wilson@example.com",
        start_datetime=datetime(2024, 1, 18, 10, 0),
        end_datetime=datetime(2024, 1, 22, 14, 0)
    )
    booking_repo.create(booking3)
    
    # Filter by datetime range (should return bookings that overlap)
    # Range: 2024-01-16 to 2024-01-21 should match booking1 and booking3
    response = client.get("/api/v1/bookings?start_datetime=2024-01-16T00:00:00&end_datetime=2024-01-21T00:00:00")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    customer_names = {b["customer_name"] for b in data}
    assert "John Doe" in customer_names
    assert "Bob Wilson" in customer_names
    assert "Jane Smith" not in customer_names


def test_get_bookings_by_car_id_and_datetime(client, sample_car):
    """Test getting bookings filtered by both car_id and datetime range."""
    # Create another car
    car2 = Car(
        brand="Honda",
        model="Accord",
        year=2024,
        color="Red",
        daily_price=32000.0,
        vin="2HGBH41JXMN109187",
        status=CarStatus.AVAILABLE,
        dealer_id=1
    )
    car2 = car_repo.create(car2)
    
    # Create bookings for both cars
    booking1 = Booking(
        car_id=sample_car.id,
        customer_name="John Doe",
        customer_email="john.doe@example.com",
        start_datetime=datetime(2024, 1, 15, 10, 0),
        end_datetime=datetime(2024, 1, 20, 14, 0)
    )
    booking_repo.create(booking1)
    
    booking2 = Booking(
        car_id=car2.id,
        customer_name="Jane Smith",
        customer_email="jane.smith@example.com",
        start_datetime=datetime(2024, 1, 16, 10, 0),
        end_datetime=datetime(2024, 1, 18, 14, 0)
    )
    booking_repo.create(booking2)
    
    # Filter by car_id and datetime range
    response = client.get(f"/api/v1/bookings?car_id={sample_car.id}&start_datetime=2024-01-14T00:00:00&end_datetime=2024-01-21T00:00:00")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["car_id"] == sample_car.id
    assert data[0]["customer_name"] == "John Doe"


def test_get_booking_by_id(client, sample_car):
    """Test getting a specific booking."""
    booking = Booking(
        car_id=sample_car.id,
        customer_name="John Doe",
        customer_email="john.doe@example.com",
        start_datetime=datetime(2024, 1, 15, 10, 0),
        end_datetime=datetime(2024, 1, 20, 14, 0)
    )
    created_booking = booking_repo.create(booking)
    
    response = client.get(f"/api/v1/bookings/{created_booking.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["customer_name"] == "John Doe"
    assert data["id"] == created_booking.id


def test_delete_booking(client, sample_car):
    """Test deleting a booking."""
    booking = Booking(
        car_id=sample_car.id,
        customer_name="John Doe",
        customer_email="john.doe@example.com",
        start_datetime=datetime(2024, 1, 15, 10, 0),
        end_datetime=datetime(2024, 1, 20, 14, 0)
    )
    created_booking = booking_repo.create(booking)
    
    response = client.delete(f"/api/v1/bookings/{created_booking.id}")
    assert response.status_code == 204
    
    # Verify booking is deleted
    response = client.get(f"/api/v1/bookings/{created_booking.id}")
    assert response.status_code == 404


def test_get_available_cars_for_date_range(client, sample_car):
    """Test getting cars available for a specific date range."""
    # Create another available car
    car2 = Car(
        brand="Honda",
        model="Accord",
        year=2024,
        color="Red",
        daily_price=32000.0,
        vin="2HGBH41JXMN109187",
        status=CarStatus.AVAILABLE,
        dealer_id=1
    )
    car2 = car_repo.create(car2)
    
    # Create a booking for sample_car that conflicts with the requested range
    booking = Booking(
        car_id=sample_car.id,
        customer_name="John Doe",
        customer_email="john.doe@example.com",
        start_datetime=datetime(2024, 1, 15, 10, 0),
        end_datetime=datetime(2024, 1, 20, 14, 0)
    )
    booking_repo.create(booking)
    
    # Request cars available for a date range that conflicts with sample_car's booking
    response = client.get("/api/v1/bookings/available-cars", params={
        "start_datetime": "2024-01-16T00:00:00",
        "end_datetime": "2024-01-18T00:00:00"
    })
    assert response.status_code == 200
    data = response.json()
    # Should only return car2 (sample_car has a conflicting booking)
    assert len(data) == 1
    assert data[0]["id"] == car2.id
    assert data[0]["brand"] == "Honda"


def test_get_available_cars_excludes_maintenance(client, sample_car):
    """Test that cars in maintenance are excluded from availability filtering."""
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
    
    # Request available cars for a date range
    response = client.get("/api/v1/bookings/available-cars", params={
        "start_datetime": "2024-01-15T00:00:00",
        "end_datetime": "2024-01-20T00:00:00"
    })
    assert response.status_code == 200
    data = response.json()
    # Should only return sample_car (maintenance_car is excluded)
    assert len(data) == 1
    assert data[0]["id"] == sample_car.id
    assert data[0]["status"] == "available"


def test_get_available_cars_invalid_date_range(client, sample_car):
    """Test that invalid date ranges (end before start) return an error."""
    response = client.get("/api/v1/bookings/available-cars", params={
        "start_datetime": "2024-01-20T00:00:00",
        "end_datetime": "2024-01-15T00:00:00"
    })
    assert response.status_code == 400
    assert "end_datetime must be after start_datetime" in response.json()["detail"]


def test_get_available_cars_no_conflicts(client, sample_car):
    """Test getting available cars when there are no booking conflicts."""
    # Create another available car
    car2 = Car(
        brand="Honda",
        model="Accord",
        year=2024,
        color="Red",
        daily_price=32000.0,
        vin="2HGBH41JXMN109187",
        status=CarStatus.AVAILABLE,
        dealer_id=1
    )
    car2 = car_repo.create(car2)
    
    # Create a booking for sample_car, but for a different date range
    booking = Booking(
        car_id=sample_car.id,
        customer_name="John Doe",
        customer_email="john.doe@example.com",
        start_datetime=datetime(2024, 2, 1, 10, 0),
        end_datetime=datetime(2024, 2, 5, 14, 0)
    )
    booking_repo.create(booking)
    
    # Request cars available for a date range that doesn't conflict
    response = client.get("/api/v1/bookings/available-cars", params={
        "start_datetime": "2024-01-15T00:00:00",
        "end_datetime": "2024-01-20T00:00:00"
    })
    assert response.status_code == 200
    data = response.json()
    # Should return both cars (no conflicts for the requested range)
    assert len(data) == 2
    car_ids = {car["id"] for car in data}
    assert sample_car.id in car_ids
    assert car2.id in car_ids


def test_get_available_cars_missing_parameters(client, sample_car):
    """Test that missing required parameters return an error."""
    # Missing end_datetime
    response = client.get("/api/v1/bookings/available-cars", params={
        "start_datetime": "2024-01-15T00:00:00"
    })
    assert response.status_code == 422  # Validation error
    
    # Missing start_datetime
    response = client.get("/api/v1/bookings/available-cars", params={
        "end_datetime": "2024-01-20T00:00:00"
    })
    assert response.status_code == 422  # Validation error

