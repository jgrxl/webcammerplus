"""Authentication service for handling OAuth flows and user authentication.

This service encapsulates all authentication-related business logic,
including OAuth callbacks, session management, and Stripe customer creation.
"""

import logging
from typing import Dict, Optional, Tuple

from flask import session

from config import get_config
from models.user import User
from services.stripe_service import StripeService
from services.user_service import UserService

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication flows and user management."""

    def __init__(
        self,
        user_service: Optional[UserService] = None,
        stripe_service: Optional[StripeService] = None,
    ) -> None:
        """Initialize the authentication service.

        Args:
            user_service: User service instance (will create if not provided)
            stripe_service: Stripe service instance (will create if not provided)
        """
        self.user_service = user_service or UserService()
        self.stripe_service = stripe_service or StripeService()
        self.config = get_config()

    def handle_oauth_callback(self, token_data: Dict) -> Tuple[User, str]:
        """Process OAuth callback and create/update user.

        This method handles the complete OAuth callback flow:
        1. Extract user info from token
        2. Create or update user in our system
        3. Create Stripe customer if needed
        4. Setup session data

        Args:
            token_data: OAuth token data from Auth0

        Returns:
            Tuple of (User instance, redirect URL)

        Raises:
            ValueError: If token data is invalid
            Exception: If user creation/update fails
        """
        # Extract user info from token
        user_info = token_data.get("userinfo")
        if not user_info:
            raise ValueError("No user info in token data")

        # Create or update user
        logger.info(f"Processing OAuth callback for user: {user_info.get('sub')}")
        user = self.user_service.create_or_update_user(user_info)

        # Create Stripe customer if needed
        if not user.stripe_customer_id:
            try:
                customer_id = self._create_stripe_customer_for_user(user)
                # Update user with Stripe customer ID
                self.user_service.update_user_subscription(
                    user.auth0_id,
                    user.subscription_tier,
                    stripe_customer_id=customer_id,
                )
                user.stripe_customer_id = customer_id
                logger.info(f"Created Stripe customer {customer_id} for user {user.auth0_id}")
            except Exception as e:
                # Log error but don't fail login
                logger.error(f"Failed to create Stripe customer for {user.auth0_id}: {e}")

        # Get redirect URL
        redirect_url = session.pop("redirect_after_login", "/")

        return user, redirect_url

    def _create_stripe_customer_for_user(self, user: User) -> str:
        """Create a Stripe customer for the user.

        Args:
            user: User instance

        Returns:
            Stripe customer ID

        Raises:
            Exception: If Stripe customer creation fails
        """
        try:
            customer = self.stripe_service.create_customer(
                user_email=user.email,
                user_name=user.name,
                auth0_id=user.auth0_id,
            )
            return customer.id
        except Exception as e:
            logger.error(f"Error creating Stripe customer: {e}")
            raise

    def setup_user_session(self, user_info: Dict, access_token: str) -> None:
        """Setup Flask session with user data.

        Args:
            user_info: User information from Auth0
            access_token: OAuth access token
        """
        session["user"] = user_info
        session["access_token"] = access_token
        logger.debug(f"Session setup for user: {user_info.get('sub')}")

    def clear_user_session(self) -> None:
        """Clear all user data from session."""
        session.clear()
        logger.debug("User session cleared")

    def get_logout_url(self, return_to: str) -> str:
        """Generate Auth0 logout URL.

        Args:
            return_to: URL to redirect to after logout

        Returns:
            Complete Auth0 logout URL
        """
        logout_url = (
            f"https://{self.config.auth0.domain}/v2/logout?"
            f"returnTo={return_to}&client_id={self.config.auth0.client_id}"
        )
        return logout_url

    def get_current_user_from_session(self) -> Optional[Dict]:
        """Get current user info from session.

        Returns:
            User info dict or None if not authenticated
        """
        return session.get("user")

    def is_user_authenticated(self) -> bool:
        """Check if user is authenticated.

        Returns:
            True if user has valid session
        """
        return "user" in session and "access_token" in session

    def store_redirect_url(self, url: str) -> None:
        """Store URL to redirect to after login.

        Args:
            url: URL to redirect to after successful login
        """
        session["redirect_after_login"] = url

    def get_user_usage_summary(self, user: User) -> Dict:
        """Get comprehensive usage summary for user.

        This is a convenience method that delegates to UserService
        but could add authentication-specific context.

        Args:
            user: User instance

        Returns:
            Usage summary dictionary
        """
        return self.user_service.get_user_usage_summary(user.auth0_id)

    def refresh_user_data(self, auth0_id: str) -> Optional[User]:
        """Refresh user data from database.

        Args:
            auth0_id: Auth0 user ID

        Returns:
            Updated User instance or None
        """
        try:
            return self.user_service.get_user_by_auth0_id(auth0_id)
        except Exception as e:
            logger.error(f"Error refreshing user data for {auth0_id}: {e}")
            return None