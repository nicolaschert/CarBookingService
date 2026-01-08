"""
In-memory database using Pydantic models.
"""
from typing import Dict, TypeVar, Generic, Optional

T = TypeVar('T')


class InMemoryDatabase(Generic[T]):
    """Generic in-memory database storage."""
    
    def __init__(self):
        self._storage: Dict[int, T] = {}
        self._next_id = 1
    
    def create(self, item: T) -> T:
        """Create a new item and assign it an ID."""
        if hasattr(item, 'id') and item.id is None:
            item.id = self._next_id
            self._next_id += 1
        elif hasattr(item, 'id') and item.id in self._storage:
            raise ValueError(f"Item with id {item.id} already exists")
        elif not hasattr(item, 'id'):
            # For items without id attribute, use next_id as key
            item_id = self._next_id
            self._next_id += 1
            self._storage[item_id] = item
            return item
        
        item_id = item.id
        self._storage[item_id] = item
        return item
    
    def get_by_id(self, item_id: int) -> Optional[T]:
        """Get an item by its ID."""
        return self._storage.get(item_id)
    
    def get_all(self) -> list[T]:
        """Get all items."""
        return list(self._storage.values())
    
    def update(self, item_id: int, item: T) -> Optional[T]:
        """Update an item by its ID."""
        if item_id not in self._storage:
            return None
        if hasattr(item, 'id'):
            item.id = item_id
        self._storage[item_id] = item
        return item
    
    def delete(self, item_id: int) -> bool:
        """Delete an item by its ID."""
        if item_id in self._storage:
            del self._storage[item_id]
            return True
        return False
    
    def exists(self, item_id: int) -> bool:
        """Check if an item exists."""
        return item_id in self._storage
    
    def clear(self):
        """Clear all items from the database."""
        self._storage.clear()
        self._next_id = 1
