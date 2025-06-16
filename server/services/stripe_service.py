import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import stripe

from models.subscription_tiers import (
    SUBSCRIPTION_TIERS,
    SubscriptionTier,
    get_tier_by_name,
)
from models.user import Subscription

logger = logging.getLogger(__name__)


class StripeService:
    """Service for handling Stripe operations."""

    def __init__(self):
        self.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
        self.stripe_publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        if not self.stripe_secret_key:
            raise ValueError("STRIPE_SECRET_KEY environment variable is required")

        stripe.api_key = self.stripe_secret_key

        # Stripe price IDs for each tier (set these in your environment)
        self.price_ids = {
            "pro_monthly": os.getenv(
                "STRIPE_PRICE_PRO_MONTHLY", "price_pro_monthly_placeholder"
            ),
            "pro_yearly": os.getenv(
                "STRIPE_PRICE_PRO_YEARLY", "price_pro_yearly_placeholder"
            ),
            "max_monthly": os.getenv(
                "STRIPE_PRICE_MAX_MONTHLY", "price_max_monthly_placeholder"
            ),
            "max_yearly": os.getenv(
                "STRIPE_PRICE_MAX_YEARLY", "price_max_yearly_placeholder"
            ),
        }

    def create_customer(
        self,
        user_email: str,
        user_name: Optional[str] = None,
        auth0_id: Optional[str] = None,
    ) -> stripe.Customer:
        """Create a new Stripe customer."""
        try:
            metadata = {}
            if auth0_id:
                metadata["auth0_id"] = auth0_id

            customer = stripe.Customer.create(
                email=user_email, name=user_name, metadata=metadata
            )

            logger.info(f"Created Stripe customer: {customer.id} for {user_email}")
            return customer

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise

    def get_customer(self, customer_id: str) -> Optional[stripe.Customer]:
        """Get Stripe customer by ID."""
        try:
            return stripe.Customer.retrieve(customer_id)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve customer {customer_id}: {e}")
            return None

    def create_checkout_session(
        self,
        customer_id: str,
        tier: SubscriptionTier,
        billing_cycle: str = "monthly",
        success_url: str = "",
        cancel_url: str = "",
    ) -> stripe.checkout.Session:
        """Create a Stripe Checkout session for subscription."""
        try:
            # Get the price ID for the tier and billing cycle
            tier_name = tier.value
            price_key = f"{tier_name}_{billing_cycle}"
            price_id = self.price_ids.get(price_key)

            if not price_id or price_id.endswith("_placeholder"):
                raise ValueError(
                    f"Price ID not configured for {tier_name} {billing_cycle}"
                )

            # Create checkout session
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={"tier": tier.value, "billing_cycle": billing_cycle},
                subscription_data={
                    "metadata": {"tier": tier.value, "billing_cycle": billing_cycle}
                },
            )

            logger.info(
                f"Created checkout session: {session.id} for {tier_name} {billing_cycle}"
            )
            return session

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session: {e}")
            raise

    def create_billing_portal_session(
        self, customer_id: str, return_url: str = ""
    ) -> stripe.billing_portal.Session:
        """Create a Stripe billing portal session."""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )

            logger.info(f"Created billing portal session for customer: {customer_id}")
            return session

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create billing portal session: {e}")
            raise

    def get_subscription(self, subscription_id: str) -> Optional[stripe.Subscription]:
        """Get Stripe subscription by ID."""
        try:
            return stripe.Subscription.retrieve(subscription_id)
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve subscription {subscription_id}: {e}")
            return None

    def cancel_subscription(
        self, subscription_id: str, at_period_end: bool = True
    ) -> stripe.Subscription:
        """Cancel a Stripe subscription."""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id, cancel_at_period_end=at_period_end
            )

            logger.info(
                f"Cancelled subscription: {subscription_id} (at_period_end: {at_period_end})"
            )
            return subscription

        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription {subscription_id}: {e}")
            raise

    def get_customer_subscriptions(self, customer_id: str) -> List[stripe.Subscription]:
        """Get all subscriptions for a customer."""
        try:
            subscriptions = stripe.Subscription.list(customer=customer_id, status="all")
            return subscriptions.data

        except stripe.error.StripeError as e:
            logger.error(f"Failed to get subscriptions for customer {customer_id}: {e}")
            return []

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Stripe webhook signature."""
        try:
            stripe.Webhook.construct_event(payload, signature, self.webhook_secret)
            return True
        except ValueError:
            logger.error("Invalid payload in webhook")
            return False
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature in webhook")
            return False

    def process_webhook_event(self, event: Dict[str, Any]) -> Optional[Subscription]:
        """Process Stripe webhook event and return subscription info if relevant."""
        event_type = event["type"]
        data_object = event["data"]["object"]

        logger.info(f"Processing webhook event: {event_type}")

        if event_type in [
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
        ]:
            return self._process_subscription_event(data_object, event_type)

        elif event_type in ["invoice.payment_succeeded", "invoice.payment_failed"]:
            return self._process_invoice_event(data_object, event_type)

        else:
            logger.info(f"Unhandled webhook event type: {event_type}")
            return None

    def _process_subscription_event(
        self, subscription_data: Dict[str, Any], event_type: str
    ) -> Optional[Subscription]:
        """Process subscription-related webhook events."""
        try:
            # Extract subscription details
            subscription_id = subscription_data["id"]
            customer_id = subscription_data["customer"]
            status = subscription_data["status"]

            # Get tier from metadata
            metadata = subscription_data.get("metadata", {})
            tier_name = metadata.get("tier", "free")
            billing_cycle = metadata.get("billing_cycle", "monthly")

            tier = get_tier_by_name(tier_name)
            if not tier:
                logger.warning(f"Unknown tier in subscription metadata: {tier_name}")
                tier = SubscriptionTier.FREE

            # Create subscription object
            subscription = Subscription(
                stripe_subscription_id=subscription_id,
                stripe_customer_id=customer_id,
                user_auth0_id="",  # Will be filled by the calling service
                tier=tier,
                status=status,
                billing_cycle=billing_cycle,
                current_period_start=datetime.fromtimestamp(
                    subscription_data["current_period_start"]
                ),
                current_period_end=datetime.fromtimestamp(
                    subscription_data["current_period_end"]
                ),
                amount=subscription_data["items"]["data"][0]["price"]["unit_amount"]
                / 100,
                currency=subscription_data["items"]["data"][0]["price"]["currency"],
            )

            # Handle cancellation
            if subscription_data.get("canceled_at"):
                subscription.canceled_at = datetime.fromtimestamp(
                    subscription_data["canceled_at"]
                )

            # Handle trial
            if subscription_data.get("trial_start"):
                subscription.trial_start = datetime.fromtimestamp(
                    subscription_data["trial_start"]
                )
            if subscription_data.get("trial_end"):
                subscription.trial_end = datetime.fromtimestamp(
                    subscription_data["trial_end"]
                )

            logger.info(
                f"Processed subscription event: {event_type} for {subscription_id}"
            )
            return subscription

        except Exception as e:
            logger.error(f"Failed to process subscription event: {e}")
            return None

    def _process_invoice_event(
        self, invoice_data: Dict[str, Any], event_type: str
    ) -> Optional[Subscription]:
        """Process invoice-related webhook events."""
        try:
            subscription_id = invoice_data.get("subscription")
            if not subscription_id:
                return None

            # Get the subscription details
            subscription = self.get_subscription(subscription_id)
            if not subscription:
                return None

            # Process based on event type
            if event_type == "invoice.payment_succeeded":
                logger.info(f"Payment succeeded for subscription: {subscription_id}")
                # Subscription should be active
                status = "active"
            elif event_type == "invoice.payment_failed":
                logger.warning(f"Payment failed for subscription: {subscription_id}")
                # Subscription might be past due
                status = "past_due"
            else:
                return None

            # Return subscription with updated status
            return self._process_subscription_event(
                subscription, "subscription.updated"
            )

        except Exception as e:
            logger.error(f"Failed to process invoice event: {e}")
            return None

    def get_pricing_info(self) -> Dict[str, Any]:
        """Get pricing information for all tiers."""
        pricing = {}

        for tier, limits in SUBSCRIPTION_TIERS.items():
            if tier == SubscriptionTier.FREE:
                continue

            pricing[tier.value] = {
                "display_name": limits.display_name,
                "monthly_price": limits.price_monthly,
                "yearly_price": limits.price_yearly,
                "features": {
                    "translations_per_month": limits.translations_per_month,
                    "replies_per_month": limits.replies_per_month,
                    "writes_per_month": limits.writes_per_month,
                    "influx_queries_per_month": limits.influx_queries_per_month,
                    "api_access": limits.api_access,
                    "priority_support": limits.priority_support,
                    "analytics_retention_days": limits.analytics_retention_days,
                    "custom_styles": limits.custom_styles,
                    "batch_operations": limits.batch_operations,
                },
            }

        return pricing
