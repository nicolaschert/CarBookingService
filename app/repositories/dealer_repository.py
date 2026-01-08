from typing import List, Optional
from app.domain.models import Dealer
from app.repositories.database import InMemoryDatabase


class DealerRepository:
    """Repository for dealer operations."""
    
    def __init__(self, db: InMemoryDatabase[Dealer]):
        self.db = db
    
    def create(self, dealer: Dealer) -> Dealer:
        """Create a new dealer."""
        return self.db.create(dealer)
    
    def get_by_id(self, dealer_id: int) -> Optional[Dealer]:
        """Get a dealer by ID."""
        return self.db.get_by_id(dealer_id)
    
    def get_all(self) -> List[Dealer]:
        """Get all dealers."""
        return self.db.get_all()
    
    def update(self, dealer_id: int, dealer: Dealer) -> Optional[Dealer]:
        """Update a dealer."""
        return self.db.update(dealer_id, dealer)
    
    def delete(self, dealer_id: int) -> bool:
        """Delete a dealer."""
        return self.db.delete(dealer_id)

