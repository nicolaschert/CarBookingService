from typing import List
from fastapi import APIRouter, HTTPException, status
from app.domain.models import Car
from app.schemas.car import CarCreate, CarUpdate, CarResponse
from app.repositories.car_repository import CarRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.dealer_repository import DealerRepository

router = APIRouter(prefix="/cars", tags=["cars"])


def get_car_repository() -> CarRepository:
    """Get car repository instance."""
    from app.main import car_repo
    return car_repo


def get_booking_repository() -> BookingRepository:
    """Get booking repository instance."""
    from app.main import booking_repo
    return booking_repo


def get_dealer_repository() -> DealerRepository:
    """Get dealer repository instance."""
    from app.main import dealer_repo
    return dealer_repo


@router.post("", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
def create_car(car_data: CarCreate):
    """Create a new car in the inventory."""
    car_repo = get_car_repository()
    dealer_repo = get_dealer_repository()
    
    # Check if dealer exists
    dealer = dealer_repo.get_by_id(car_data.dealer_id)
    if not dealer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dealer with id {car_data.dealer_id} not found"
        )
    
    # Check if VIN already exists
    existing_car = car_repo.get_by_vin(car_data.vin)
    if existing_car:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Car with VIN {car_data.vin} already exists"
        )
    
    car = Car(**car_data.model_dump())
    created_car = car_repo.create(car)
    return CarResponse.model_validate(created_car)


@router.get("", response_model=List[CarResponse])
def get_cars():
    """Get all cars."""
    car_repo = get_car_repository()
    cars = car_repo.get_all()
    return [CarResponse.model_validate(car) for car in cars]


@router.get("/{car_id}", response_model=CarResponse)
def get_car(car_id: int):
    """Get a specific car by ID."""
    car_repo = get_car_repository()
    car = car_repo.get_by_id(car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {car_id} not found"
        )
    return CarResponse.model_validate(car)


@router.put("/{car_id}", response_model=CarResponse)
def update_car(car_id: int, car_data: CarUpdate):
    """Update a car."""
    car_repo = get_car_repository()
    
    existing_car = car_repo.get_by_id(car_id)
    if not existing_car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {car_id} not found"
        )
    
    # Check if dealer exists if dealer_id is being updated
    if car_data.dealer_id and car_data.dealer_id != existing_car.dealer_id:
        dealer_repo = get_dealer_repository()
        dealer = dealer_repo.get_by_id(car_data.dealer_id)
        if not dealer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dealer with id {car_data.dealer_id} not found"
            )
    
    # Check VIN uniqueness if VIN is being updated
    if car_data.vin and car_data.vin != existing_car.vin:
        car_with_vin = car_repo.get_by_vin(car_data.vin)
        if car_with_vin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Car with VIN {car_data.vin} already exists"
            )
    
    # Update only provided fields
    update_data = car_data.model_dump(exclude_unset=True)
    updated_car = existing_car.model_copy(update=update_data)
    updated_car = car_repo.update(car_id, updated_car)
    
    return CarResponse.model_validate(updated_car)


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(car_id: int):
    """Delete a car."""
    car_repo = get_car_repository()
    booking_repo = get_booking_repository()
    
    car = car_repo.get_by_id(car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {car_id} not found"
        )
    
    # Check if car has active bookings
    bookings = booking_repo.get_by_car_id(car_id)
    if bookings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete car with id {car_id}: it has {len(bookings)} active booking(s)"
        )
    
    car_repo.delete(car_id)
