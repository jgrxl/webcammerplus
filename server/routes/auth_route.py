from dataclasses import asdict

from flask import Response, abort, jsonify, redirect, request, session, url_for
from flask_restx import Namespace, Resource, fields

from services.stripe_service import StripeService
from services.user_service import UserService
from utils.auth import requires_auth, setup_oauth

api = Namespace("auth", description="Authentication and user management")

# Response models
user_response_model = api.model(
    "UserResponse",
    {
        "auth0_id": fields.String(description="Auth0 user ID"),
        "email": fields.String(description="User email"),
        "name": fields.String(description="User name"),
        "picture": fields.String(description="User profile picture URL"),
        "email_verified": fields.Boolean(description="Email verification status"),
        "subscription_tier": fields.String(description="Current subscription tier"),
        "subscription_status": fields.String(description="Subscription status"),
        "created_at": fields.String(description="Account creation date"),
        "last_login": fields.String(description="Last login date"),
    },
)

usage_response_model = api.model(
    "UsageResponse",
    {
        "tier": fields.String(description="Subscription tier"),
        "tier_display_name": fields.String(description="Human-readable tier name"),
        "subscription_status": fields.String(description="Subscription status"),
        "current_period_start": fields.String(
            description="Current billing period start"
        ),
        "usage": fields.Raw(description="Usage statistics and limits"),
        "features": fields.Raw(description="Available features"),
    },
)

error_model = api.model("Error", {"error": fields.String(description="Error message")})


@api.route("/profile")
class UserProfile(Resource):
    @api.response(200, "Success", user_response_model)
    @api.response(401, "Unauthorized", error_model)
    @api.doc("get_user_profile")
    @requires_auth
    def get(self):
        """Get current user's profile information"""
        try:
            user = request.user
            return jsonify(user.to_dict())
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@api.route("/usage")
class UserUsage(Resource):
    @api.response(200, "Success", usage_response_model)
    @api.response(401, "Unauthorized", error_model)
    @api.doc("get_user_usage")
    @requires_auth
    def get(self):
        """Get current user's usage statistics and limits"""
        try:
            user = request.user
            user_service = UserService()
            usage_summary = user_service.get_user_usage_summary(user.auth0_id)
            return jsonify(usage_summary)
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@api.route("/pricing")
class PricingInfo(Resource):
    @api.response(200, "Success")
    @api.doc("get_pricing_info")
    def get(self):
        """Get pricing information for all subscription tiers"""
        try:
            stripe_service = StripeService()
            pricing = stripe_service.get_pricing_info()
            return jsonify(pricing)
        except Exception as e:
            return jsonify({"error": str(e)}), 500


# OAuth routes (these won't be documented in Swagger as they're redirects)
def setup_auth_routes(app, auth0):
    """Setup OAuth routes that aren't part of the API namespace."""

    @app.route("/auth/login")
    def login():
        """Initiate Auth0 login flow."""
        # Get the redirect URL from query params or use default
        redirect_uri = request.args.get(
            "redirect_uri", url_for("auth_callback", _external=True)
        )
        session["redirect_after_login"] = request.args.get("return_to", "/")

        return auth0.authorize_redirect(redirect_uri)

    @app.route("/auth/callback")
    def auth_callback():
        """Handle Auth0 callback after login."""
        try:
            # Get the access token
            token = auth0.authorize_access_token()

            # Get user info
            user_info = token.get("userinfo")
            if not user_info:
                # Fallback to calling userinfo endpoint
                user_info = auth0.parse_id_token(token)

            # Create or update user
            user_service = UserService()
            user = user_service.create_or_update_user(user_info)

            # Store auth info in session
            session["user"] = user_info
            session["access_token"] = token["access_token"]

            # Create Stripe customer if doesn't exist
            if not user.stripe_customer_id:
                try:
                    stripe_service = StripeService()
                    customer = stripe_service.create_customer(
                        user_email=user.email,
                        user_name=user.name,
                        auth0_id=user.auth0_id,
                    )

                    # Update user with Stripe customer ID
                    user_service.update_user_subscription(
                        user.auth0_id,
                        user.subscription_tier,
                        stripe_customer_id=customer.id,
                    )
                except Exception as e:
                    # Log error but don't fail login
                    app.logger.error(f"Failed to create Stripe customer: {e}")

            # Redirect to the original destination
            redirect_url = session.pop("redirect_after_login", "/")
            return redirect(redirect_url)

        except Exception as e:
            app.logger.error(f"Auth callback error: {e}")
            return redirect("/?error=auth_failed")

    @app.route("/auth/logout")
    def logout():
        """Clear session and redirect to Auth0 logout."""
        session.clear()

        # Get return URL
        return_to = request.args.get("return_to", request.host_url)

        # Auth0 logout URL
        from utils.auth import Auth0Config

        config = Auth0Config()
        logout_url = (
            f"https://{config.domain}/v2/logout?"
            + f"returnTo={return_to}&client_id={config.client_id}"
        )

        return redirect(logout_url)

    @app.route("/auth/user")
    def get_user():
        """Get current user from session (for frontend)."""
        user_info = session.get("user")
        if user_info:
            return jsonify(user_info)
        else:
            return jsonify({"error": "Not authenticated"}), 401
