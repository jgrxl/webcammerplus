from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SubscriptionTier(Enum):
    """Subscription tier enumeration."""

    FREE = "free"
    PRO = "pro"
    MAX = "max"


@dataclass(frozen=True)
class TierLimits:
    """Limits and features for each subscription tier."""

    name: str
    display_name: str
    price_monthly: float  # USD
    price_yearly: float  # USD
    stripe_price_id_monthly: Optional[str]
    stripe_price_id_yearly: Optional[str]

    # Feature limits
    translations_per_month: int
    replies_per_month: int
    writes_per_month: int
    influx_queries_per_month: int

    # Features
    api_access: bool
    priority_support: bool
    analytics_retention_days: int
    custom_styles: bool
    batch_operations: bool


# Define subscription tiers with their limits and features
SUBSCRIPTION_TIERS = {
    SubscriptionTier.FREE: TierLimits(
        name="free",
        display_name="Free",
        price_monthly=0.0,
        price_yearly=0.0,
        stripe_price_id_monthly=None,
        stripe_price_id_yearly=None,
        # Generous free tier limits
        translations_per_month=100,
        replies_per_month=50,
        writes_per_month=25,
        influx_queries_per_month=100,
        # Basic features
        api_access=True,
        priority_support=False,
        analytics_retention_days=7,
        custom_styles=False,
        batch_operations=False,
    ),
    SubscriptionTier.PRO: TierLimits(
        name="pro",
        display_name="Pro",
        price_monthly=9.99,
        price_yearly=99.99,  # 2 months free
        stripe_price_id_monthly="price_1Ra0jT2YXvKFVM7Kadjo2hpX",  # Pro Monthly
        stripe_price_id_yearly="price_1Ra0l92YXvKFVM7KJ6qswPzY",  # Pro Yearly
        # Pro tier limits
        translations_per_month=2000,
        replies_per_month=1000,
        writes_per_month=500,
        influx_queries_per_month=2000,
        # Pro features
        api_access=True,
        priority_support=True,
        analytics_retention_days=30,
        custom_styles=True,
        batch_operations=True,
    ),
    SubscriptionTier.MAX: TierLimits(
        name="max",
        display_name="Max",
        price_monthly=29.99,
        price_yearly=299.99,  # 2 months free
        stripe_price_id_monthly="price_1Ra0kp2YXvKFVM7KE9lP5UhK",  # Max Monthly
        stripe_price_id_yearly="price_1Ra0kp2YXvKFVM7K2PFvTAOY",  # Max Yearly
        # Max tier limits (unlimited)
        translations_per_month=-1,  # -1 means unlimited
        replies_per_month=-1,
        writes_per_month=-1,
        influx_queries_per_month=-1,
        # Max features
        api_access=True,
        priority_support=True,
        analytics_retention_days=365,
        custom_styles=True,
        batch_operations=True,
    ),
}


def get_tier_limits(tier: SubscriptionTier) -> TierLimits:
    """Get limits for a specific subscription tier."""
    return SUBSCRIPTION_TIERS[tier]


def get_tier_by_name(name: str) -> Optional[SubscriptionTier]:
    """Get subscription tier by name string."""
    for tier in SubscriptionTier:
        if tier.value == name.lower():
            return tier
    return None


def is_usage_within_limits(
    tier: SubscriptionTier,
    translations: int = 0,
    replies: int = 0,
    writes: int = 0,
    influx_queries: int = 0,
) -> bool:
    """Check if current usage is within tier limits."""
    limits = get_tier_limits(tier)

    # Check each limit (-1 means unlimited)
    if (
        limits.translations_per_month != -1
        and translations > limits.translations_per_month
    ):
        return False
    if limits.replies_per_month != -1 and replies > limits.replies_per_month:
        return False
    if limits.writes_per_month != -1 and writes > limits.writes_per_month:
        return False
    if (
        limits.influx_queries_per_month != -1
        and influx_queries > limits.influx_queries_per_month
    ):
        return False

    return True


def can_access_feature(tier: SubscriptionTier, feature: str) -> bool:
    """Check if a tier has access to a specific feature."""
    limits = get_tier_limits(tier)

    feature_map = {
        "api_access": limits.api_access,
        "priority_support": limits.priority_support,
        "custom_styles": limits.custom_styles,
        "batch_operations": limits.batch_operations,
    }

    return feature_map.get(feature, False)
