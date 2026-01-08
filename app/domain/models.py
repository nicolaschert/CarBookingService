from datetime import date, datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator, ConfigDict


class CarStatus(str, Enum):
    """Car status enumeration."""
    AVAILABLE = "available"
    MAINTENANCE = "maintenance"


class Dealer(BaseModel):
    """Domain model for a dealer."""
    id: Optional[int] = None
    name: str = Field(..., min_length=1)
    location: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Oscar Mobility Downtown",
                "location": "New York, NY"
            }
        }
    )


class Car(BaseModel):
    """Domain model for a car in the dealership inventory."""
    id: Optional[int] = None
    brand: str
    model: str
    year: int = Field(..., gt=1900, le=date.today().year + 1)
    color: str
    daily_price: float = Field(..., gt=0)
    vin: str = Field(..., min_length=17, max_length=17)
    status: CarStatus = CarStatus.AVAILABLE
    dealer_id: int = Field(..., gt=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "brand": "Toyota",
                "model": "Camry",
                "year": 2023,
                "color": "Blue",
                "daily_price": 35000.0,
                "vin": "1HGBH41JXMN109186",
                "status": "available",
                "dealer_id": 1
            }
        }
    )


class Booking(BaseModel):
    """Domain model for a car booking."""
    id: Optional[int] = None
    car_id: int
    customer_name: str = Field(..., min_length=1)
    customer_email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    start_datetime: datetime
    end_datetime: datetime

    @model_validator(mode='after')
    def validate_datetimes(self):
        """Validate that end_datetime is after start_datetime."""
        if self.end_datetime <= self.start_datetime:
            raise ValueError("end_datetime must be after start_datetime")
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "car_id": 1,
                "customer_name": "John Doe",
                "customer_email": "john.doe@example.com",
                "start_datetime": "2024-01-15T10:00:00",
                "end_datetime": "2024-01-20T14:00:00"
            }
        }
    )
