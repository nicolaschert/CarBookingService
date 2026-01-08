from fastapi import FastAPI
from app.api.router import api_router
from app.domain.models import Car, Booking, Dealer
from app.repositories.database import InMemoryDatabase
from app.repositories.car_repository import CarRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.dealer_repository import DealerRepository

# Initialize in-memory databases
car_db = InMemoryDatabase[Car]()
booking_db = InMemoryDatabase[Booking]()
dealer_db = InMemoryDatabase[Dealer]()

# Initialize repositories
car_repo = CarRepository(car_db)
booking_repo = BookingRepository(booking_db)
dealer_repo = DealerRepository(dealer_db)

# Create initial dealer if database is empty
if not dealer_repo.get_all():
    initial_dealer = Dealer(
        name="Oscar Mobility Main",
        location="Munich, Germany"
    )
    dealer_repo.create(initial_dealer)

# Create FastAPI application
app = FastAPI(
    title="Oscar Mobility Dealership API",
    description="API for managing car inventory and date-based bookings",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

