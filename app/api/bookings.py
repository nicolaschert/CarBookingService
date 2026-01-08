from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Query  # pyright: ignore[reportMissingImports]
from app.domain.models import Booking, CarStatus
from app.schemas.booking import BookingCreate, BookingResponse
from app.schemas.car import CarResponse
from app.repositories.car_repository import CarRepository
from app.repositories.booking_repository import BookingRepository

router = APIRouter(prefix="/bookings", tags=["bookings"])


def get_car_repository() -> CarRepository:
    """Get car repository instance."""
    from app.main import car_repo
    return car_repo


def get_booking_repository() -> BookingRepository:
    """Get booking repository instance."""
    from app.main import booking_repo
    return booking_repo


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(booking_data: BookingCreate):
    """Create a new booking."""
    car_repo = get_car_repository()
    booking_repo = get_booking_repository()
    
    # Check if car exists
    car = car_repo.get_by_id(booking_data.car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {booking_data.car_id} not found"
        )
    
    # Check if car is available
    if car.status != CarStatus.AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Car with id {booking_data.car_id} is not available (status: {car.status.value})"
        )
    
    # Check for conflicting bookings
    if booking_repo.has_conflicting_booking(
        booking_data.car_id,
        booking_data.start_datetime,
        booking_data.end_datetime
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Car with id {booking_data.car_id} is already booked for the selected time period"
        )
    
    booking = Booking(**booking_data.model_dump())
    created_booking = booking_repo.create(booking)
    return BookingResponse.model_validate(created_booking)


@router.get("", response_model=List[BookingResponse])
def get_bookings(
    car_id: Optional[int] = Query(None, description="Filter bookings by car ID"),
    start_datetime: Optional[datetime] = Query(None, description="Filter bookings that start on or after this datetime"),
    end_datetime: Optional[datetime] = Query(None, description="Filter bookings that end on or before this datetime")
):
    """Get all bookings, optionally filtered by car ID and/or datetime range.
    
    Filters can be combined:
    - car_id: Returns bookings for a specific car
    - start_datetime: Returns bookings that start on or after this datetime
    - end_datetime: Returns bookings that end on or before this datetime
    - start_datetime + end_datetime: Returns bookings that overlap with the datetime range
    """
    booking_repo = get_booking_repository()
    
    # Get bookings filtered by car_id if provided
    if car_id:
        bookings = booking_repo.get_by_car_id(car_id)
    else:
        bookings = booking_repo.get_all()
    
    # Apply datetime filters if provided
    if start_datetime is not None or end_datetime is not None:
        datetime_filtered = booking_repo.get_by_datetime_range(start_datetime, end_datetime)
        # Intersect with car_id filtered results if car_id was provided
        if car_id:
            datetime_ids = {b.id for b in datetime_filtered}
            bookings = [b for b in bookings if b.id in datetime_ids]
        else:
            bookings = datetime_filtered
    
    return [BookingResponse.model_validate(booking) for booking in bookings]


@router.get("/available-cars", response_model=List[CarResponse])
def get_available_cars(
    start_datetime: datetime = Query(..., description="Filter cars available from this datetime"),
    end_datetime: datetime = Query(..., description="Filter cars available until this datetime")
):
    """Get cars available for a specific date range.
    
    Returns only cars that:
    - Have status 'available' (not in maintenance)
    - Don't have conflicting bookings for the specified datetime range
    """
    car_repo = get_car_repository()
    booking_repo = get_booking_repository()
    
    # Validate that end_datetime is after start_datetime
    if end_datetime <= start_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_datetime must be after start_datetime"
        )
    
    cars = car_repo.get_all()
    available_cars = []
    
    for car in cars:
        # Check if car is available (not in maintenance)
        if car.status != CarStatus.AVAILABLE:
            continue
        
        # Check if car has conflicting bookings for the requested date range
        if not booking_repo.has_conflicting_booking(
            car.id,
            start_datetime,
            end_datetime
        ):
            available_cars.append(car)
    
    return [CarResponse.model_validate(car) for car in available_cars]


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int):
    """Get a specific booking by ID."""
    booking_repo = get_booking_repository()
    booking = booking_repo.get_by_id(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with id {booking_id} not found"
        )
    return BookingResponse.model_validate(booking)


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(booking_id: int):
    """Cancel a booking."""
    booking_repo = get_booking_repository()
    
    booking = booking_repo.get_by_id(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with id {booking_id} not found"
        )
    
    booking_repo.delete(booking_id)

