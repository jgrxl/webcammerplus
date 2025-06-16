import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from models.subscription_tiers import (
    SubscriptionTier,
    get_tier_limits,
    is_usage_within_limits,
)
from models.user import Subscription, User

logger = logging.getLogger(__name__)


class UserService:
    """Service for managing users and their subscriptions."""

    def __init__(self):
        # In-memory storage for now (replace with database later)
        self._users: Dict[str, User] = {}
        self._subscriptions: Dict[str, Subscription] = {}

    def create_or_update_user(self, auth0_profile: Dict[str, Any]) -> User:
        """Create a new user or update existing user from Auth0 profile."""
        auth0_id = auth0_profile.get("sub")
        if not auth0_id:
            raise ValueError("Auth0 profile missing 'sub' field")

        existing_user = self._users.get(auth0_id)

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

            logger.info(f"Updated existing user: {auth0_id}")
            return existing_user
        else:
            # Create new user
            user = User.from_auth0_profile(auth0_profile)
            user.last_login = datetime.utcnow()
            self._users[auth0_id] = user

            logger.info(f"Created new user: {auth0_id}")
            return user

    def get_user(self, auth0_id: str) -> Optional[User]:
        """Get user by Auth0 ID."""
        user = self._users.get(auth0_id)
        if user and user.needs_usage_reset():
            user.reset_monthly_usage()
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        for user in self._users.values():
            if user.email == email:
                if user.needs_usage_reset():
                    user.reset_monthly_usage()
                return user
        return None

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

        logger.info(f"Updated subscription for user {auth0_id} to {tier.value}")
        return user

    def check_usage_limits(
        self, auth0_id: str, operation: str, increment: int = 1
    ) -> tuple[bool, Optional[str]]:
        """Check if user can perform operation within their tier limits."""
        user = self.get_user(auth0_id)
        if not user:
            return False, "User not found"

        if not user.is_subscription_active():
            return False, "Subscription is not active"

        # Get current usage
        current_usage = {
            "translations": user.translations_used,
            "replies": user.replies_used,
            "writes": user.writes_used,
            "influx_queries": user.influx_queries_used,
        }

        # Add the increment for this operation
        if operation in current_usage:
            current_usage[operation] += increment
        else:
            return False, f"Unknown operation: {operation}"

        # Check against limits
        is_within_limits = is_usage_within_limits(
            user.subscription_tier,
            translations=current_usage["translations"],
            replies=current_usage["replies"],
            writes=current_usage["writes"],
            influx_queries=current_usage["influx_queries"],
        )

        if not is_within_limits:
            limits = get_tier_limits(user.subscription_tier)
            operation_limit = getattr(limits, f"{operation}_per_month", 0)
            if operation_limit == -1:
                operation_limit = "unlimited"
            return (
                False,
                f"Usage limit exceeded. Your {user.subscription_tier.value} plan allows {operation_limit} {operation} per month",
            )

        return True, None

    def increment_usage(self, auth0_id: str, operation: str, amount: int = 1) -> bool:
        """Increment user's usage counter for an operation."""
        user = self.get_user(auth0_id)
        if not user:
            return False

        # Increment the appropriate counter
        if operation == "translations":
            user.translations_used += amount
        elif operation == "replies":
            user.replies_used += amount
        elif operation == "writes":
            user.writes_used += amount
        elif operation == "influx_queries":
            user.influx_queries_used += amount
        else:
            logger.warning(f"Unknown operation for usage increment: {operation}")
            return False

        user.updated_at = datetime.utcnow()
        logger.debug(f"Incremented {operation} usage by {amount} for user {auth0_id}")
        return True

    def get_user_usage_summary(self, auth0_id: str) -> Dict[str, Any]:
        """Get user's current usage and limits."""
        user = self.get_user(auth0_id)
        if not user:
            return {}

        limits = get_tier_limits(user.subscription_tier)

        return {
            "tier": user.subscription_tier.value,
            "tier_display_name": limits.display_name,
            "subscription_status": user.subscription_status,
            "current_period_start": user.current_period_start.isoformat(),
            "usage": {
                "translations": {
                    "used": user.translations_used,
                    "limit": (
                        limits.translations_per_month
                        if limits.translations_per_month != -1
                        else "unlimited"
                    ),
                },
                "replies": {
                    "used": user.replies_used,
                    "limit": (
                        limits.replies_per_month
                        if limits.replies_per_month != -1
                        else "unlimited"
                    ),
                },
                "writes": {
                    "used": user.writes_used,
                    "limit": (
                        limits.writes_per_month
                        if limits.writes_per_month != -1
                        else "unlimited"
                    ),
                },
                "influx_queries": {
                    "used": user.influx_queries_used,
                    "limit": (
                        limits.influx_queries_per_month
                        if limits.influx_queries_per_month != -1
                        else "unlimited"
                    ),
                },
            },
            "features": {
                "api_access": limits.api_access,
                "priority_support": limits.priority_support,
                "analytics_retention_days": limits.analytics_retention_days,
                "custom_styles": limits.custom_styles,
                "batch_operations": limits.batch_operations,
            },
        }

    def list_users(self) -> List[Dict[str, Any]]:
        """Get list of all users (admin function)."""
        return [user.to_dict() for user in self._users.values()]

    def create_subscription(self, subscription: Subscription) -> Subscription:
        """Create a new subscription record."""
        self._subscriptions[subscription.stripe_subscription_id] = subscription
        logger.info(f"Created subscription: {subscription.stripe_subscription_id}")
        return subscription

    def get_subscription(self, stripe_subscription_id: str) -> Optional[Subscription]:
        """Get subscription by Stripe subscription ID."""
        return self._subscriptions.get(stripe_subscription_id)

    def get_subscription_by_customer(
        self, stripe_customer_id: str
    ) -> Optional[Subscription]:
        """Get subscription by Stripe customer ID."""
        for subscription in self._subscriptions.values():
            if subscription.stripe_customer_id == stripe_customer_id:
                return subscription
        return None

    def update_subscription_status(
        self,
        stripe_subscription_id: str,
        status: str,
        current_period_start: Optional[datetime] = None,
        current_period_end: Optional[datetime] = None,
    ) -> Optional[Subscription]:
        """Update subscription status from Stripe webhook."""
        subscription = self.get_subscription(stripe_subscription_id)
        if not subscription:
            return None

        subscription.status = status
        if current_period_start:
            subscription.current_period_start = current_period_start
        if current_period_end:
            subscription.current_period_end = current_period_end

        # Update the user's subscription info
        user = self.get_user(subscription.user_auth0_id)
        if user:
            user.subscription_status = status
            if current_period_end:
                user.subscription_end_date = current_period_end
            user.updated_at = datetime.utcnow()

        logger.info(
            f"Updated subscription status: {stripe_subscription_id} -> {status}"
        )
        return subscription
