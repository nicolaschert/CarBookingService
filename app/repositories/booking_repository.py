from datetime import datetime
from typing import List, Optional
from app.domain.models import Booking
from app.repositories.database import InMemoryDatabase


class BookingRepository:
    """Repository for booking operations."""
    
    def __init__(self, db: InMemoryDatabase[Booking]):
        self.db = db
    
    def create(self, booking: Booking) -> Booking:
        """Create a new booking."""
        return self.db.create(booking)
    
    def get_by_id(self, booking_id: int) -> Optional[Booking]:
        """Get a booking by ID."""
        return self.db.get_by_id(booking_id)
    
    def get_all(self) -> List[Booking]:
        """Get all bookings."""
        return self.db.get_all()
    
    def get_by_car_id(self, car_id: int) -> List[Booking]:
        """Get all bookings for a specific car."""
        bookings = self.db.get_all()
        return [booking for booking in bookings if booking.car_id == car_id]

    def get_by_datetime_range(
        self,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None
    ) -> List[Booking]:
        """Get bookings filtered by datetime range.
        
        Returns bookings that overlap with the specified datetime range.
        If only start_datetime is provided, returns bookings that start on or after it.
        If only end_datetime is provided, returns bookings that end on or before it.
        If both are provided, returns bookings that overlap with the range.
        """
        bookings = self.db.get_all()
        
        if start_datetime is None and end_datetime is None:
            return bookings
        
        filtered = []
        for booking in bookings:
            if start_datetime is not None and end_datetime is not None:
                # Check if booking overlaps with the specified range
                # Overlap occurs if: booking.start < filter_end AND booking.end > filter_start
                if booking.start_datetime < end_datetime and booking.end_datetime > start_datetime:
                    filtered.append(booking)
            elif start_datetime is not None:
                # Filter: bookings that start on or after start_datetime
                if booking.start_datetime >= start_datetime:
                    filtered.append(booking)
            elif end_datetime is not None:
                # Filter: bookings that end on or before end_datetime
                if booking.end_datetime <= end_datetime:
                    filtered.append(booking)
        
        return filtered

    def has_conflicting_booking(
        self, 
        car_id: int, 
        start_datetime: datetime, 
        end_datetime: datetime,
        exclude_booking_id: Optional[int] = None
    ) -> bool:
        """Check if there's a conflicting booking for the given car and datetimes."""
        car_bookings = self.get_by_car_id(car_id)
        
        for booking in car_bookings:
            if exclude_booking_id and booking.id == exclude_booking_id:
                continue
            
            # Check for overlap: booking conflicts if datetimes overlap
            if not (end_datetime <= booking.start_datetime or start_datetime >= booking.end_datetime):
                return True
        
        return False
    
    def delete(self, booking_id: int) -> bool:
        """Delete a booking."""
        return self.db.delete(booking_id)

