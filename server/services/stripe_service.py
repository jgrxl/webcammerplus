import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import stripe

from config import get_config
from models.subscription_tiers import (
    SUBSCRIPTION_TIERS,
    SubscriptionTier,
    get_tier_by_name,
)
from models.user import Subscription

logger = logging.getLogger(__name__)
config = get_config()


class StripeService:
    """Service for handling Stripe operations."""

    def __init__(self):
        self.stripe_secret_key = config.stripe.secret_key
        self.stripe_publishable_key = config.stripe.publishable_key
        self.webhook_secret = config.stripe.webhook_secret

        if not self.stripe_secret_key:
            raise ValueError("STRIPE_SECRET_KEY is required in configuration")

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

    def handle_checkout_session_creation(
        self,
        user,
        tier_name: str,
        billing_cycle: str,
        success_url: str,
        cancel_url: str,
    ) -> Dict[str, str]:
        """Handle the complete checkout session creation flow.
        
        Args:
            user: User object
            tier_name: Subscription tier name
            billing_cycle: Billing cycle (monthly/yearly)
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel
            
        Returns:
            Dict with checkout_url and session_id
            
        Raises:
            ValueError: If validation fails
            Exception: If checkout creation fails
        """
        from models.subscription_tiers import get_tier_by_name, SubscriptionTier
        from services.user_service import UserService
        
        # Validate tier
        tier = get_tier_by_name(tier_name)
        if not tier or tier == SubscriptionTier.FREE:
            raise ValueError("Invalid subscription tier")
        
        # Validate billing cycle
        if billing_cycle not in ["monthly", "yearly"]:
            raise ValueError("Invalid billing cycle")
        
        # Check if user already has an active subscription
        if user.subscription_tier != SubscriptionTier.FREE and user.is_subscription_active():
            raise ValueError("User already has an active subscription")
        
        # Ensure user has Stripe customer ID
        if not user.stripe_customer_id:
            customer = self.create_customer(
                user_email=user.email,
                user_name=user.name,
                auth0_id=user.auth0_id,
            )
            
            # Update user with customer ID
            user_service = UserService()
            user_service.update_user_subscription(
                user.auth0_id,
                user.subscription_tier,
                stripe_customer_id=customer.id,
            )
            user.stripe_customer_id = customer.id
        
        # Create checkout session
        session = self.create_checkout_session(
            customer_id=user.stripe_customer_id,
            tier=tier,
            billing_cycle=billing_cycle,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        
        return {
            "checkout_url": session.url,
            "session_id": session.id,
        }

    def handle_subscription_cancellation(self, user) -> Dict[str, Any]:
        """Handle the complete subscription cancellation flow.
        
        Args:
            user: User object
            
        Returns:
            Dict with cancellation details
            
        Raises:
            ValueError: If no active subscription
            Exception: If cancellation fails
        """
        from models.subscription_tiers import SubscriptionTier
        
        if user.subscription_tier == SubscriptionTier.FREE:
            raise ValueError("No active subscription to cancel")
        
        if not user.stripe_customer_id:
            raise ValueError("No Stripe customer found")
        
        # Find active subscription
        subscriptions = self.get_customer_subscriptions(user.stripe_customer_id)
        
        active_sub = None
        for sub in subscriptions:
            if sub.status in ["active", "trialing"]:
                active_sub = sub
                break
        
        if not active_sub:
            raise ValueError("No active subscription found")
        
        # Cancel subscription at period end
        cancelled_sub = self.cancel_subscription(active_sub.id, at_period_end=True)
        
        return {
            "message": "Subscription will be cancelled at the end of the current period",
            "cancel_at_period_end": cancelled_sub.cancel_at_period_end,
            "current_period_end": cancelled_sub.current_period_end,
        }

    def handle_webhook_event(
        self, payload: bytes, signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle the complete webhook event processing flow.
        
        Args:
            payload: Raw webhook payload
            signature: Stripe signature header
            
        Returns:
            Dict with status and any relevant data
            
        Raises:
            ValueError: If signature verification fails
        """
        from services.user_service import UserService
        
        # Skip signature verification in development if no webhook secret is configured
        if signature and self.webhook_secret:
            # Verify webhook signature
            if not self.verify_webhook_signature(payload, signature):
                raise ValueError("Invalid webhook signature")
        else:
            logger.warning("⚠️  Webhook signature verification skipped (development mode)")
        
        # Parse event
        try:
            import json
            event_data = json.loads(payload)
            event = stripe.Event.construct_from(event_data, stripe.api_key)
        except ValueError:
            raise ValueError("Invalid webhook payload")
        
        # Process event
        subscription_data = self.process_webhook_event(event.to_dict())
        
        if subscription_data:
            # Update user subscription in our system
            user_service = UserService()
            
            # Find user by Stripe customer ID
            stripe_customer_id = subscription_data.stripe_customer_id
            
            # Get customer from Stripe to find Auth0 ID
            customer = self.get_customer(stripe_customer_id)
            if customer and customer.metadata.get("auth0_id"):
                auth0_id = customer.metadata["auth0_id"]
                
                # Update user subscription
                user_service.update_user_subscription(
                    auth0_id=auth0_id,
                    tier=subscription_data.tier,
                    stripe_customer_id=stripe_customer_id,
                    subscription_start=subscription_data.current_period_start,
                    subscription_end=subscription_data.current_period_end,
                    status=subscription_data.status,
                )
                
                # Store subscription record
                subscription_data.user_auth0_id = auth0_id
                user_service.create_subscription(subscription_data)
        
        return {"status": "success"}

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
            elif event_type == "invoice.payment_failed":
                logger.warning(f"Payment failed for subscription: {subscription_id}")
                # Subscription might be past due
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
