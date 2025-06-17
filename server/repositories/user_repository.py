import logging
from datetime import datetime
from typing import Dict, List, Optional

from models.user import User

from .base_repository import BaseRepository, InMemoryRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """Repository interface for User entities."""

    def find_by_auth0_id(self, auth0_id: str) -> Optional[User]:
        """Find a user by their Auth0 ID.

        Args:
            auth0_id: The Auth0 identifier

        Returns:
            The user if found, None otherwise
        """
        raise NotImplementedError

    def find_by_email(self, email: str) -> Optional[User]:
        """Find a user by their email.

        Args:
            email: The user's email

        Returns:
            The user if found, None otherwise
        """
        raise NotImplementedError

    def find_by_stripe_customer_id(self, stripe_customer_id: str) -> Optional[User]:
        """Find a user by their Stripe customer ID.

        Args:
            stripe_customer_id: The Stripe customer identifier

        Returns:
            The user if found, None otherwise
        """
        raise NotImplementedError

    def find_active_subscribers(self) -> List[User]:
        """Find all users with active subscriptions.

        Returns:
            List of users with active subscriptions
        """
        raise NotImplementedError

    def update_usage(self, auth0_id: str, operation: str, increment: int = 1) -> bool:
        """Update usage statistics for a user.

        Args:
            auth0_id: The Auth0 identifier
            operation: The operation type
            increment: The amount to increment

        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError


class InMemoryUserRepository(InMemoryRepository[User], UserRepository):
    """In-memory implementation of UserRepository."""

    def __init__(self):
        super().__init__()
        # Additional indexes for efficient lookups
        self._email_index: Dict[str, str] = {}  # email -> auth0_id
        self._stripe_index: Dict[str, str] = {}  # stripe_customer_id -> auth0_id

    def find_by_id(self, id: str) -> Optional[User]:
        """Override to use auth0_id as primary key."""
        return self.find_by_auth0_id(id)

    def find_by_auth0_id(self, auth0_id: str) -> Optional[User]:
        return self._storage.get(auth0_id)

    def find_by_email(self, email: str) -> Optional[User]:
        auth0_id = self._email_index.get(email)
        if auth0_id:
            return self._storage.get(auth0_id)
        return None

    def find_by_stripe_customer_id(self, stripe_customer_id: str) -> Optional[User]:
        auth0_id = self._stripe_index.get(stripe_customer_id)
        if auth0_id:
            return self._storage.get(auth0_id)
        return None

    def find_active_subscribers(self) -> List[User]:
        active_users = []
        for user in self._storage.values():
            if user.is_subscription_active():
                active_users.append(user)
        return active_users

    def save(self, entity: User) -> User:
        """Save user and update indexes."""
        # Update indexes
        if entity.email:
            self._email_index[entity.email] = entity.auth0_id
        if entity.stripe_customer_id:
            self._stripe_index[entity.stripe_customer_id] = entity.auth0_id

        # Save to main storage
        self._storage[entity.auth0_id] = entity
        return entity

    def delete(self, id: str) -> bool:
        """Delete user and clean up indexes."""
        user = self._storage.get(id)
        if user:
            # Remove from indexes
            if user.email and user.email in self._email_index:
                del self._email_index[user.email]
            if (
                user.stripe_customer_id
                and user.stripe_customer_id in self._stripe_index
            ):
                del self._stripe_index[user.stripe_customer_id]

            # Remove from storage
            del self._storage[id]
            return True
        return False

    def update_usage(self, auth0_id: str, operation: str, increment: int = 1) -> bool:
        """Update usage statistics for a user."""
        user = self.find_by_auth0_id(auth0_id)
        if not user:
            return False

        # Initialize usage dict if needed
        if not hasattr(user, "usage") or user.usage is None:
            user.usage = {}

        # Update the specific operation count
        if operation not in user.usage:
            user.usage[operation] = 0
        user.usage[operation] += increment

        # Update last activity
        user.last_activity = datetime.utcnow()

        # Save the updated user
        self.save(user)
        logger.info(f"Updated usage for user {auth0_id}: {operation} +{increment}")

        return True

    def clear(self):
        """Clear all data including indexes."""
        super().clear()
        self._email_index.clear()
        self._stripe_index.clear()


# Future database implementations can be added here:
# class SQLAlchemyUserRepository(UserRepository):
#     """SQLAlchemy implementation of UserRepository."""
#     pass
#
# class MongoDBUserRepository(UserRepository):
#     """MongoDB implementation of UserRepository."""
#     pass
