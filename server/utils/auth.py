import os
import jwt
import logging
from functools import wraps
from typing import Optional, Dict, Any, Callable
from flask import request, jsonify, current_app
from authlib.integrations.flask_client import OAuth
from services.user_service import UserService


logger = logging.getLogger(__name__)


class Auth0Config:
    """Auth0 configuration helper."""
    
    def __init__(self):
        self.domain = os.getenv('AUTH0_DOMAIN', 'dev-4xh5xi1xfh7w7y2n.us.auth0.com')
        self.client_id = os.getenv('AUTH0_CLIENT_ID', '57sIYSODLSDddlyQVokooAFjTEHDNRYo')
        self.client_secret = os.getenv('AUTH0_CLIENT_SECRET')
        self.audience = os.getenv('AUTH0_AUDIENCE', 'https://dev-4xh5xi1xfh7w7y2n.us.auth0.com/api/v2/')  # Auth0 Management API
        self.algorithms = ['RS256']
        
        if not all([self.domain, self.client_id]):
            raise ValueError("Missing required Auth0 environment variables (domain, client_id)")
    
    @property
    def issuer(self) -> str:
        """Get Auth0 issuer URL."""
        return f"https://{self.domain}/"
    
    @property
    def jwks_url(self) -> str:
        """Get JWKS URL for token verification."""
        return f"https://{self.domain}/.well-known/jwks.json"


class AuthError(Exception):
    """Custom Auth exception."""
    
    def __init__(self, error: Dict[str, str], status_code: int):
        self.error = error
        self.status_code = status_code


def get_token_auth_header() -> str:
    """Extract access token from Authorization header."""
    auth = request.headers.get('Authorization', None)
    
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)
    
    parts = auth.split()
    
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)
    
    if len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)
    
    if len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)
    
    return parts[1]


def verify_decode_jwt(token: str, config: Auth0Config) -> Dict[str, Any]:
    """Verify and decode JWT token."""
    # Get the public key from Auth0
    import requests
    
    try:
        # Get JWKS
        jwks_response = requests.get(config.jwks_url)
        jwks_response.raise_for_status()
        jwks = jwks_response.json()
        
        # Get the key ID from token header
        unverified_header = jwt.get_unverified_header(token)
        
        # Find the right key
        rsa_key = {}
        for key in jwks['keys']:
            if key['kid'] == unverified_header['kid']:
                rsa_key = {
                    'kty': key['kty'],
                    'kid': key['kid'],
                    'use': key['use'],
                    'n': key['n'],
                    'e': key['e']
                }
                break
        
        if not rsa_key:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find a suitable key.'
            }, 400)
        
        # Verify token
        from jwt import PyJWKClient
        jwks_client = PyJWKClient(config.jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # Decode with or without audience validation
        decode_options = {
            'algorithms': config.algorithms,
            'issuer': config.issuer,
        }
        
        # Only add audience if it's configured
        if config.audience:
            decode_options['audience'] = config.audience
        
        payload = jwt.decode(
            token,
            signing_key.key,
            **decode_options
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise AuthError({
            'code': 'token_expired',
            'description': 'Token expired.'
        }, 401)
    
    except jwt.JWTClaimsError:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Incorrect claims. Please, check the audience and issuer.'
        }, 401)
    
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Unable to parse authentication token.'
        }, 400)


def requires_auth(f: Callable) -> Callable:
    """Decorator to require valid Auth0 JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            config = Auth0Config()
            token = get_token_auth_header()
            payload = verify_decode_jwt(token, config)
            
            # Add user info to request context
            request.current_user = payload
            
            # Create or update user in our system
            user_service = UserService()
            user = user_service.create_or_update_user(payload)
            request.user = user
            
        except AuthError as e:
            return jsonify(e.error), e.status_code
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return jsonify({
                'code': 'authentication_failed',
                'description': 'Authentication failed.'
            }), 500
        
        return f(*args, **kwargs)
    
    return decorated


def requires_subscription(min_tier: str = 'free') -> Callable:
    """Decorator to require specific subscription tier."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            # This decorator should be used after @requires_auth
            if not hasattr(request, 'user'):
                return jsonify({
                    'error': 'Authentication required'
                }), 401
            
            user = request.user
            
            # Check if subscription is active
            if not user.is_subscription_active():
                return jsonify({
                    'error': 'Active subscription required',
                    'subscription_status': user.subscription_status
                }), 403
            
            # Check tier level (simple comparison for now)
            tier_levels = {'free': 0, 'pro': 1, 'max': 2}
            user_level = tier_levels.get(user.subscription_tier.value, 0)
            required_level = tier_levels.get(min_tier, 0)
            
            if user_level < required_level:
                return jsonify({
                    'error': f'Subscription tier "{min_tier}" or higher required',
                    'current_tier': user.subscription_tier.value
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


def check_usage_limits(operation: str, increment: int = 1) -> Callable:
    """Decorator to check and enforce usage limits."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs):
            # This decorator should be used after @requires_auth
            if not hasattr(request, 'user'):
                return jsonify({
                    'error': 'Authentication required'
                }), 401
            
            user = request.user
            user_service = UserService()
            
            # Check usage limits
            can_proceed, error_message = user_service.check_usage_limits(
                user.auth0_id, operation, increment
            )
            
            if not can_proceed:
                return jsonify({
                    'error': error_message,
                    'usage_exceeded': True
                }), 429  # Too Many Requests
            
            # Execute the function
            result = f(*args, **kwargs)
            
            # Increment usage counter after successful execution
            user_service.increment_usage(user.auth0_id, operation, increment)
            
            return result
        
        return decorated
    return decorator


def setup_oauth(app) -> OAuth:
    """Setup OAuth for Auth0 integration."""
    oauth = OAuth(app)
    
    config = Auth0Config()
    
    auth0 = oauth.register(
        'auth0',
        client_id=config.client_id,
        client_secret=config.client_secret,
        server_metadata_url=f'https://{config.domain}/.well-known/openid_configuration',
        client_kwargs={
            'scope': 'openid profile email',
        },
    )
    
    return oauth, auth0