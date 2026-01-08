from typing import List, Optional
from app.domain.models import Car
from app.repositories.database import InMemoryDatabase


class CarRepository:
    """Repository for car operations."""
    
    def __init__(self, db: InMemoryDatabase[Car]):
        self.db = db
    
    def create(self, car: Car) -> Car:
        """Create a new car."""
        return self.db.create(car)
    
    def get_by_id(self, car_id: int) -> Optional[Car]:
        """Get a car by ID."""
        return self.db.get_by_id(car_id)
    
    def get_all(self) -> List[Car]:
        """Get all cars."""
        return self.db.get_all()
    
    def update(self, car_id: int, car: Car) -> Optional[Car]:
        """Update a car."""
        return self.db.update(car_id, car)
    
    def delete(self, car_id: int) -> bool:
        """Delete a car."""
        return self.db.delete(car_id)
    
    def get_by_vin(self, vin: str) -> Optional[Car]:
        """Get a car by VIN."""
        cars = self.db.get_all()
        for car in cars:
            if car.vin == vin:
                return car
        return None

