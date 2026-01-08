# Oscar Mobility Dealership API - Inventory & Calendar Availability System (Option 1)


This is a service for managing a dealership's car inventory and date-based bookings.


## Features
- **Car Inventory Management**: Create, read, update, and delete cars
- **Date-based Bookings**: Check availability and book cars for specific date ranges with conflict detection
- **In-Memory Database**: Pydantic-based in-memory storage
- **RESTful API**: Clean REST endpoints with proper HTTP status codes
- **Comprehensive Tests**: Unit and integration tests included

## Technology Stack
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running FastAPI
- **Pytest**: Testing framework

## API Endpoints

### Cars

- `POST /api/v1/cars` - Create a new car (that will be available for booking)
- `GET /api/v1/cars` - Get all cars
- `GET /api/v1/cars/{car_id}` - Get a specific car
- `PUT /api/v1/cars/{car_id}` - Update a car
- `DELETE /api/v1/cars/{car_id}` - Delete a car

### Bookings

- `POST /api/v1/bookings` - Create a new booking
- `GET /api/v1/bookings` - Get all bookings (optional query: `car_id={id}`)
- `GET /api/v1/bookings/{booking_id}` - Get a specific booking
- `DELETE /api/v1/bookings/{booking_id}` - Cancel a booking

### Bookings > Available Cars
- `GET /api/v1/bookings/available-cars?start_datetime={start_datetime}&end_datetime={end_datetime}` - Get available cars for a certain date period

## Setup instructions

### Instalation

1. Create and activate a virtual environment (with python 3.13.5):
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs


## Key design decisions
- **In-memory Database**: The backend uses a custom, generic in-memory Pydantic-based database, making it easy to prototype and test without persistent storage or external dependencies. This is meant for demonstration; all data is transient and lost on restart. This simplifies deployment and development but is unsuitable for production.

- **Repository Pattern**: Data access is abstracted using repository classes for `Car`, `Dealer`, and `Booking`. This helps encapsulate business logic, keeps route handlers clean, and supports future backend changes (e.g., moving to a real database).

- **Strict Schemas & Validation**: This service uses Pydantic models and FastAPI schemas to enforce type safety and validate data, including custom validators for fields like VIN (Vehicle Identification Number) and booking dates.

- **Booking Date Logic**: Booking objects use datetime fields and validate at the schema level to prevent invalid date ranges (end before start, etc).

- **Modular API Structure**: The API is split into logical route files (`cars.py`, `bookings.py`, etc.) to keep concerns separated.


## Tradeoffs
### Why FastAPI over Django or Flask?
Django or Flask may be preferable when you need a monolithic web app, server-rendered templates, or a huge ecosystem, but for robust, quick, and type-safe API backends, FastAPI offers major advantages.

### Why use an in-memory database instead of SQLite or PostgreSQL?
In-memory databases are a simpler and quicker way to build and demo APIs when you don't need to keep your data.

### Why use a REST API instead of a CLI or Python functions?
A REST API turns your functionality into a reusable, network-accessible service, opening it to clients/frontends instead of restricting it to a single machine or developer environment. It is closer to a real production service. For anything multi-user, automated, or collaborative, an API would be the best choice.


## Changes needed for production
To make this project suitable for production deployment, several important changes are needed:

- **Replace In-Memory Database with Persistent Storage**  
   This includes:
   - Using an ORM such as SQLAlchemy or Tortoise ORM.
   - Handling database connection pooling and migrations.
   This will also address concurrency, multi-process safety.

- **Implement Authentication and Authorization**  

- **Data Validation and Error Handling**  
   Ensure all user input is strictly validated (beyond type checks).

- **Production-Ready Server**  
   Use a production-grade ASGI server such as Uvicorn or Hypercorn with proper worker management (e.g., via Gunicorn or systemd). Configure timeouts, keep-alives, and health checks.

- **Containerization**  
  Add container configuration (e.g., Dockerfile, docker-compose) for reproducible deployments and environment consistency.

- Some other aspects to take into account: 
  - **Rate Limiting and Abuse Protection**  
  - **Input/Output Sanitization and Security**  
  - **Logging, Monitoring, and Traceability**  
  - **Configuration Management**  

## Assumptions
The following assumptions were made in the creation of this project:

- **Single-Dealer Scope**: The prototype is intended for a single dealership instance ("Oscar Mobility Main") for demonstration purposes. Multi-dealer or franchise logic should be implemented.

- **Dealer Relationship**: Each car references a `dealer_id`. One car is assigned to one dealer. Bookings reference a `car_id`. One booking has only one car associated. All relationships are validated at creation time to prevent orphan records.

- **No User or Customer Model**: There is no concept of individual users or customer accounts in this prototype; customer is identified by it's email. 

- **No Payment Integration**: All financial or payment aspects are omitted.


## Project Structure

```
OscarMobility/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py           # API router configuration
│   │   ├── cars.py             # Car endpoints
│   │   └── bookings.py         # Booking endpoints
│   ├── domain/
│   │   ├── __init__.py
│   │   └── models.py           # Domain models (Car, Booking)
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── database.py         # In-memory database implementation
│   │   ├── car_repository.py   # Car repository
│   │   └── booking_repository.py # Booking repository
│   └── schemas/
│       ├── __init__.py
│       ├── car.py              # Car request/response schemas
│       └── booking.py          # Booking request/response schemas
├── tests/
│   ├── __init__.py
│   ├── test_cars.py            # Car endpoint tests
│   ├── test_bookings.py        # Booking endpoint tests
│   └── test_integration.py     # Integration tests
├── requirements.txt
├── pytest.ini
└── README.md
```

## Example Usage

### Create a Car

```bash
curl -X POST "http://localhost:8000/api/v1/cars" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Toyota",
    "model": "Camry",
    "year": 2023,
    "color": "Blue",
    "daily_price": 35000.0,
    "vin": "1HGBH41JXMN109186",
    "dealer_id": 1
  }'
```

### Create a Booking

```bash
curl -X POST "http://localhost:8000/api/v1/bookings" \
  -H "Content-Type: application/json" \
  -d '{
    "car_id": 1,
    "customer_name": "John D",
    "customer_email": "john@example.com",
    "start_datetime": "2026-01-15T00:00:00Z",
    "end_datetime": "2026-01-20T00:00:00Z"
  }'
```

### Get Available Cars

```bash
curl "http://localhost:8000/api/v1/bookings/available-cars?start_datetime=2024-06-20T10:00:00Z&end_datetime=2024-06-22T18:00:00Z"
```

### Get Bookings for a Car

```bash
curl "http://localhost:8000/api/v1/bookings?car_id=1"
```

## Running Tests

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_cars.py
```

