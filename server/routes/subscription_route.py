import stripe
from flask import request
from flask_restx import Namespace, Resource, fields

from core.dependencies import get_dependency
from models.subscription_tiers import SubscriptionTier, get_tier_by_name
from services.stripe_service import StripeService
from services.user_service import UserService
from utils.auth import requires_auth

api = Namespace("subscription", description="Subscription management")

# Request models
checkout_request_model = api.model(
    "CheckoutRequest",
    {
        "tier": fields.String(
            required=True,
            description="Subscription tier (pro, max)",
            enum=["pro", "max"],
        ),
        "billing_cycle": fields.String(
            required=True,
            description="Billing cycle",
            enum=["monthly", "yearly"],
            default="monthly",
        ),
        "success_url": fields.String(
            required=True, description="URL to redirect after successful payment"
        ),
        "cancel_url": fields.String(
            required=True, description="URL to redirect if payment is cancelled"
        ),
    },
)

# Response models
checkout_response_model = api.model(
    "CheckoutResponse",
    {
        "checkout_url": fields.String(description="Stripe Checkout session URL"),
        "session_id": fields.String(description="Stripe Checkout session ID"),
    },
)

billing_portal_response_model = api.model(
    "BillingPortalResponse",
    {"portal_url": fields.String(description="Stripe billing portal URL")},
)

subscription_response_model = api.model(
    "SubscriptionResponse",
    {
        "tier": fields.String(description="Current subscription tier"),
        "status": fields.String(description="Subscription status"),
        "billing_cycle": fields.String(description="Billing cycle"),
        "current_period_start": fields.String(description="Current period start date"),
        "current_period_end": fields.String(description="Current period end date"),
        "cancel_at_period_end": fields.Boolean(
            description="Whether subscription will cancel at period end"
        ),
        "amount": fields.Float(description="Subscription amount"),
        "currency": fields.String(description="Currency code"),
    },
)

error_model = api.model("Error", {"error": fields.String(description="Error message")})


@api.route("/checkout")
class CreateCheckout(Resource):
    @api.expect(checkout_request_model)
    @api.response(200, "Success", checkout_response_model)
    @api.response(400, "Bad Request", error_model)
    @api.response(401, "Unauthorized", error_model)
    @api.doc("create_checkout_session")
    @requires_auth
    def post(self):
        """Create Stripe checkout session for subscription"""
        try:
            user = request.user
            payload = request.get_json(force=True) or {}

            # Validate request
            tier_name = payload.get("tier")
            billing_cycle = payload.get("billing_cycle", "monthly")
            success_url = payload.get("success_url")
            cancel_url = payload.get("cancel_url")

            if not all([tier_name, success_url, cancel_url]):
                return {"error": "Missing required fields"}, 400

            # Use StripeService to handle checkout creation
            stripe_service = get_dependency(StripeService)
            result = stripe_service.handle_checkout_session_creation(
                user=user,
                tier_name=tier_name,
                billing_cycle=billing_cycle,
                success_url=success_url,
                cancel_url=cancel_url,
            )

            return result

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500


@api.route("/billing-portal")
class BillingPortal(Resource):
    @api.response(200, "Success", billing_portal_response_model)
    @api.response(400, "Bad Request", error_model)
    @api.response(401, "Unauthorized", error_model)
    @api.doc("create_billing_portal_session")
    @requires_auth
    def post(self):
        """Create Stripe billing portal session"""
        try:
            user = request.user
            payload = request.get_json(force=True) or {}
            return_url = payload.get("return_url", "")

            if not user.stripe_customer_id:
                return {"error": "No Stripe customer found"}, 400

            stripe_service = get_dependency(StripeService)
            session = stripe_service.create_billing_portal_session(
                customer_id=user.stripe_customer_id, return_url=return_url
            )

            return {"portal_url": session.url}

        except Exception as e:
            return {"error": str(e)}, 500


@api.route("/status")
class SubscriptionStatus(Resource):
    @api.response(200, "Success", subscription_response_model)
    @api.response(401, "Unauthorized", error_model)
    @api.doc("get_subscription_status")
    @requires_auth
    def get(self):
        """Get current subscription status"""
        try:
            user = request.user

            if user.subscription_tier == SubscriptionTier.FREE:
                return {
                    "tier": "free",
                    "status": "active",
                    "billing_cycle": None,
                    "current_period_start": None,
                    "current_period_end": None,
                    "cancel_at_period_end": False,
                    "amount": 0.0,
                    "currency": "usd",
                }

            # Get subscription details from Stripe
            if user.stripe_customer_id:
                stripe_service = get_dependency(StripeService)
                subscriptions = stripe_service.get_customer_subscriptions(
                    user.stripe_customer_id
                )

                if subscriptions:
                    # Get the most recent active subscription
                    active_sub = None
                    for sub in subscriptions:
                        if sub.status in ["active", "trialing", "past_due"]:
                            active_sub = sub
                            break

                    if active_sub:
                        return {
                            "tier": user.subscription_tier.value,
                            "status": active_sub.status,
                            "billing_cycle": active_sub.metadata.get(
                                "billing_cycle", "monthly"
                            ),
                            "current_period_start": active_sub.current_period_start,
                            "current_period_end": active_sub.current_period_end,
                            "cancel_at_period_end": active_sub.cancel_at_period_end,
                            "amount": active_sub.items.data[0].price.unit_amount
                            / 100,
                            "currency": active_sub.items.data[0].price.currency,
                        }

            # Fallback to user data
            return {
                "tier": user.subscription_tier.value,
                "status": user.subscription_status,
                "billing_cycle": None,
                "current_period_start": (
                    user.subscription_start_date.isoformat()
                    if user.subscription_start_date
                    else None
                ),
                "current_period_end": (
                    user.subscription_end_date.isoformat()
                    if user.subscription_end_date
                    else None
                ),
                "cancel_at_period_end": False,
                "amount": 0.0,
                "currency": "usd",
            }

        except Exception as e:
            return {"error": str(e)}, 500


@api.route("/cancel")
class CancelSubscription(Resource):
    @api.response(200, "Success")
    @api.response(400, "Bad Request", error_model)
    @api.response(401, "Unauthorized", error_model)
    @api.doc("cancel_subscription")
    @requires_auth
    def post(self):
        """Cancel current subscription (at period end)"""
        try:
            user = request.user

            # Use StripeService to handle cancellation
            stripe_service = get_dependency(StripeService)
            result = stripe_service.handle_subscription_cancellation(user)

            return result

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500


@api.route("/webhook")
class StripeWebhook(Resource):
    @api.doc(False)  # Hide from Swagger docs
    def post(self):
        """Handle Stripe webhook events"""
        try:
            payload = request.get_data()
            signature = request.headers.get("Stripe-Signature")

            # Use StripeService to handle the webhook
            stripe_service = get_dependency(StripeService)
            result = stripe_service.handle_webhook_event(payload, signature)

            return result

        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": str(e)}, 500
