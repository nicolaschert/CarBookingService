from datetime import datetime
from pydantic import BaseModel, Field, model_validator, ConfigDict


class BookingCreate(BaseModel):
    """Schema for creating a new booking."""
    car_id: int = Field(..., gt=0)
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


class BookingResponse(BaseModel):
    """Schema for booking response."""
    id: int
    car_id: int
    customer_name: str
    customer_email: str
    start_datetime: datetime
    end_datetime: datetime

    model_config = ConfigDict(from_attributes=True)

