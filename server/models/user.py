from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

from models.subscription_tiers import SubscriptionTier


@dataclass
class User:
    """User model for Auth0 authenticated users."""

    # Auth0 fields
    auth0_id: str  # Auth0 user ID (sub claim)
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    email_verified: bool = False

    # App-specific fields
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    # Subscription info
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    stripe_customer_id: Optional[str] = None
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None
    subscription_status: str = "active"  # active, canceled, past_due, incomplete

    # Usage tracking (reset monthly)
    current_period_start: datetime = field(default_factory=datetime.utcnow)
    translations_used: int = 0
    replies_used: int = 0
    writes_used: int = 0
    influx_queries_used: int = 0

    # User preferences
    preferences: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for JSON serialization."""
        return {
            "auth0_id": self.auth0_id,
            "email": self.email,
            "name": self.name,
            "picture": self.picture,
            "email_verified": self.email_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "subscription_tier": self.subscription_tier.value,
            "stripe_customer_id": self.stripe_customer_id,
            "subscription_start_date": (
                self.subscription_start_date.isoformat()
                if self.subscription_start_date
                else None
            ),
            "subscription_end_date": (
                self.subscription_end_date.isoformat()
                if self.subscription_end_date
                else None
            ),
            "subscription_status": self.subscription_status,
            "current_period_start": (
                self.current_period_start.isoformat()
                if self.current_period_start
                else None
            ),
            "usage": {
                "translations_used": self.translations_used,
                "replies_used": self.replies_used,
                "writes_used": self.writes_used,
                "influx_queries_used": self.influx_queries_used,
            },
            "preferences": self.preferences,
        }

    @classmethod
    def from_auth0_profile(cls, profile: Dict[str, Any]) -> "User":
        """Create User from Auth0 profile data."""
        return cls(
            auth0_id=profile.get("sub"),
            email=profile.get("email"),
            name=profile.get("name"),
            picture=profile.get("picture"),
            email_verified=profile.get("email_verified", False),
        )

    def is_subscription_active(self) -> bool:
        """Check if user has an active subscription."""
        if self.subscription_tier == SubscriptionTier.FREE:
            return True

        if self.subscription_status not in ["active", "trialing"]:
            return False

        if (
            self.subscription_end_date
            and datetime.utcnow() > self.subscription_end_date
        ):
            return False

        return True

    def needs_usage_reset(self) -> bool:
        """Check if monthly usage needs to be reset."""
        now = datetime.utcnow()
        # Reset if it's been more than 30 days since current period start
        return (now - self.current_period_start).days >= 30

    def reset_monthly_usage(self) -> None:
        """Reset monthly usage counters."""
        self.current_period_start = datetime.utcnow()
        self.translations_used = 0
        self.replies_used = 0
        self.writes_used = 0
        self.influx_queries_used = 0
        self.updated_at = datetime.utcnow()


@dataclass
class Subscription:
    """Subscription model for tracking Stripe subscriptions."""

    stripe_subscription_id: str
    stripe_customer_id: str
    user_auth0_id: str

    # Subscription details
    tier: SubscriptionTier
    status: str  # active, canceled, past_due, incomplete, trialing
    billing_cycle: str  # monthly, yearly

    # Dates
    created_at: datetime = field(default_factory=datetime.utcnow)
    current_period_start: datetime = field(default_factory=datetime.utcnow)
    current_period_end: datetime = field(default_factory=datetime.utcnow)
    canceled_at: Optional[datetime] = None
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None

    # Pricing
    amount: float = 0.0
    currency: str = "usd"

    def to_dict(self) -> Dict[str, Any]:
        """Convert subscription to dictionary for JSON serialization."""
        return {
            "stripe_subscription_id": self.stripe_subscription_id,
            "stripe_customer_id": self.stripe_customer_id,
            "user_auth0_id": self.user_auth0_id,
            "tier": self.tier.value,
            "status": self.status,
            "billing_cycle": self.billing_cycle,
            "created_at": self.created_at.isoformat(),
            "current_period_start": self.current_period_start.isoformat(),
            "current_period_end": self.current_period_end.isoformat(),
            "canceled_at": self.canceled_at.isoformat() if self.canceled_at else None,
            "trial_start": self.trial_start.isoformat() if self.trial_start else None,
            "trial_end": self.trial_end.isoformat() if self.trial_end else None,
            "amount": self.amount,
            "currency": self.currency,
        }

    def is_active(self) -> bool:
        """Check if subscription is currently active."""
        return self.status in ["active", "trialing"]

    def is_in_trial(self) -> bool:
        """Check if subscription is in trial period."""
        if not self.trial_start or not self.trial_end:
            return False

        now = datetime.utcnow()
        return self.trial_start <= now <= self.trial_end
