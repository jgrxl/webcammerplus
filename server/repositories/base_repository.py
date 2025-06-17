from abc import ABC, abstractmethod
from typing import Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base class for repository pattern implementation."""

    @abstractmethod
    def find_by_id(self, id: str) -> Optional[T]:
        """Find an entity by its ID.

        Args:
            id: The unique identifier

        Returns:
            The entity if found, None otherwise
        """

    @abstractmethod
    def find_all(self) -> List[T]:
        """Find all entities.

        Returns:
            List of all entities
        """

    @abstractmethod
    def save(self, entity: T) -> T:
        """Save or update an entity.

        Args:
            entity: The entity to save

        Returns:
            The saved entity
        """

    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete an entity by ID.

        Args:
            id: The unique identifier

        Returns:
            True if deleted, False if not found
        """

    @abstractmethod
    def exists(self, id: str) -> bool:
        """Check if an entity exists.

        Args:
            id: The unique identifier

        Returns:
            True if exists, False otherwise
        """


class InMemoryRepository(BaseRepository[T]):
    """In-memory implementation of the repository pattern."""

    def __init__(self):
        self._storage: Dict[str, T] = {}

    def find_by_id(self, id: str) -> Optional[T]:
        return self._storage.get(id)

    def find_all(self) -> List[T]:
        return list(self._storage.values())

    def save(self, entity: T) -> T:
        # Assumes the entity has an 'id' attribute
        entity_id = getattr(entity, "id", None) or getattr(entity, "auth0_id", None)
        if not entity_id:
            raise ValueError("Entity must have an 'id' or 'auth0_id' attribute")
        self._storage[entity_id] = entity
        return entity

    def delete(self, id: str) -> bool:
        if id in self._storage:
            del self._storage[id]
            return True
        return False

    def exists(self, id: str) -> bool:
        return id in self._storage

    def clear(self):
        """Clear all stored entities (useful for testing)."""
        self._storage.clear()
