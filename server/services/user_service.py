import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from models.subscription_tiers import (
    SubscriptionTier,
    get_tier_limits,
    is_usage_within_limits,
)
from models.user import User
from repositories.user_repository import InMemoryUserRepository, UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """Service for managing users and their subscriptions using repository pattern."""

    def __init__(self, repository: Optional[UserRepository] = None):
        """Initialize UserService with a repository.

        Args:
            repository: UserRepository implementation. Defaults to InMemoryUserRepository.
        """
        self.repository = repository or InMemoryUserRepository()

    def create_or_update_user(self, auth0_profile: Dict[str, Any]) -> User:
        """Create a new user or update existing user from Auth0 profile."""
        auth0_id = auth0_profile.get("sub")
        if not auth0_id:
            raise ValueError("Auth0 profile missing 'sub' field")

        existing_user = self.repository.find_by_auth0_id(auth0_id)

        if existing_user:
            # Update existing user
            existing_user.email = auth0_profile.get("email", existing_user.email)
            existing_user.name = auth0_profile.get("name", existing_user.name)
            existing_user.picture = auth0_profile.get("picture", existing_user.picture)
            existing_user.email_verified = auth0_profile.get(
                "email_verified", existing_user.email_verified
            )
            existing_user.last_login = datetime.utcnow()
            existing_user.updated_at = datetime.utcnow()

            # Reset usage if needed
            if existing_user.needs_usage_reset():
                existing_user.reset_monthly_usage()

            self.repository.save(existing_user)
            logger.info(f"Updated existing user: {auth0_id}")
            return existing_user
        else:
            # Create new user
            user = User.from_auth0_profile(auth0_profile)
            user.last_login = datetime.utcnow()
            self.repository.save(user)

            logger.info(f"Created new user: {auth0_id}")
            return user

    def get_user(self, auth0_id: str) -> Optional[User]:
        """Get user by Auth0 ID."""
        user = self.repository.find_by_auth0_id(auth0_id)
        if user and user.needs_usage_reset():
            user.reset_monthly_usage()
            self.repository.save(user)
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        user = self.repository.find_by_email(email)
        if user and user.needs_usage_reset():
            user.reset_monthly_usage()
            self.repository.save(user)
        return user

    def get_user_by_stripe_customer_id(self, stripe_customer_id: str) -> Optional[User]:
        """Get user by Stripe customer ID."""
        user = self.repository.find_by_stripe_customer_id(stripe_customer_id)
        if user and user.needs_usage_reset():
            user.reset_monthly_usage()
            self.repository.save(user)
        return user

    def update_user_subscription(
        self,
        auth0_id: str,
        tier: SubscriptionTier,
        stripe_customer_id: Optional[str] = None,
        subscription_start: Optional[datetime] = None,
        subscription_end: Optional[datetime] = None,
        status: str = "active",
    ) -> User:
        """Update user's subscription information."""
        user = self.get_user(auth0_id)
        if not user:
            raise ValueError(f"User not found: {auth0_id}")

        user.subscription_tier = tier
        user.stripe_customer_id = stripe_customer_id
        user.subscription_start_date = subscription_start
        user.subscription_end_date = subscription_end
        user.subscription_status = status
        user.updated_at = datetime.utcnow()

        self.repository.save(user)
        logger.info(f"Updated subscription for user {auth0_id} to {tier.value}")
        return user

    def check_usage_limits(
        self, auth0_id: str, operation: str, increment: int = 1
    ) -> Tuple[bool, Optional[str]]:
        """Check if user can perform operation within their tier limits."""
        user = self.get_user(auth0_id)
        if not user:
            return False, "User not found"

        if not user.is_subscription_active():
            return False, "Subscription is not active"

        # Get tier limits
        limits = get_tier_limits(user.subscription_tier)
        if not limits:
            return False, "Invalid subscription tier"

        # Check if operation would exceed limits
        current_usage = user.usage.get(operation, 0) if user.usage else 0
        projected_usage = current_usage + increment

        within_limits, exceeded_limit = is_usage_within_limits(
            {operation: projected_usage}, limits
        )

        if not within_limits:
            limit_value = getattr(limits, exceeded_limit, "N/A")
            return (
                False,
                f"Usage limit exceeded for {exceeded_limit}. Limit: {limit_value}, "
                f"Current: {current_usage}, Requested: {increment}",
            )

        return True, None

    def increment_usage(
        self, auth0_id: str, operation: str, increment: int = 1
    ) -> bool:
        """Increment usage counter for a user operation."""
        return self.repository.update_usage(auth0_id, operation, increment)

    def get_usage_stats(self, auth0_id: str) -> Dict[str, Any]:
        """Get usage statistics for a user."""
        user = self.get_user(auth0_id)
        if not user:
            return {}

        limits = get_tier_limits(user.subscription_tier)
        if not limits:
            return {}

        stats = {
            "subscription_tier": user.subscription_tier.value,
            "usage_reset_date": user.usage_reset_date.isoformat()
            if user.usage_reset_date
            else None,
            "current_usage": user.usage or {},
            "limits": {
                "translations_per_month": limits.translations_per_month,
                "replies_per_month": limits.replies_per_month,
                "writings_per_month": limits.writings_per_month,
                "max_text_length": limits.max_text_length,
                "chaturbate_connections": limits.chaturbate_connections,
            },
            "usage_percentage": {},
        }

        # Calculate usage percentages
        if user.usage:
            for operation, count in user.usage.items():
                limit_attr = f"{operation}s_per_month"
                if hasattr(limits, limit_attr):
                    limit = getattr(limits, limit_attr)
                    if limit and limit != -1:
                        stats["usage_percentage"][operation] = round(
                            (count / limit) * 100, 2
                        )

        return stats

    def get_all_users(self) -> List[User]:
        """Get all users."""
        return self.repository.find_all()

    def get_active_subscribers(self) -> List[User]:
        """Get all users with active subscriptions."""
        return self.repository.find_active_subscribers()

    def delete_user(self, auth0_id: str) -> bool:
        """Delete a user."""
        return self.repository.delete(auth0_id)
