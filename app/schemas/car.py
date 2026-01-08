from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.domain.models import CarStatus


class CarCreate(BaseModel):
    """Schema for creating a new car."""
    brand: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    year: int = Field(..., gt=1900, le=date.today().year + 1)
    color: str = Field(..., min_length=1)
    daily_price: float = Field(..., gt=0)
    vin: str = Field(..., min_length=17, max_length=17)
    status: CarStatus = CarStatus.AVAILABLE
    dealer_id: int = Field(..., gt=0)


class CarUpdate(BaseModel):
    """Schema for updating a car."""
    brand: Optional[str] = Field(None, min_length=1)
    model: Optional[str] = Field(None, min_length=1)
    year: Optional[int] = Field(None, gt=1900, le=date.today().year + 1)
    color: Optional[str] = Field(None, min_length=1)
    daily_price: Optional[float] = Field(None, gt=0)
    vin: Optional[str] = Field(None, min_length=17, max_length=17)
    status: Optional[CarStatus] = None
    dealer_id: Optional[int] = Field(None, gt=0)


class CarResponse(BaseModel):
    """Schema for car response."""
    id: int
    brand: str
    model: str
    year: int
    color: str
    daily_price: float
    vin: str
    status: CarStatus
    dealer_id: int

    model_config = ConfigDict(from_attributes=True)

