from fastapi import APIRouter
from app.api import cars, bookings

api_router = APIRouter()

api_router.include_router(cars.router)
api_router.include_router(bookings.router)
