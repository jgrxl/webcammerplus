import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class Auth0Config:
    """Auth0 configuration settings."""

    domain: str
    client_id: str
    client_secret: str
    audience: str
    algorithms: list = field(default_factory=lambda: ["RS256"])

    @property
    def issuer(self) -> str:
        """Get the Auth0 issuer URL."""
        return f"https://{self.domain}/"

    @property
    def jwks_uri(self) -> str:
        """Get the JWKS URI for token validation."""
        return f"https://{self.domain}/.well-known/jwks.json"

    @property
    def authorization_url(self) -> str:
        """Get the authorization endpoint URL."""
        return f"https://{self.domain}/authorize"

    @property
    def token_url(self) -> str:
        """Get the token endpoint URL."""
        return f"https://{self.domain}/oauth/token"


@dataclass
class StripeConfig:
    """Stripe configuration settings."""

    secret_key: str
    webhook_secret: str
    publishable_key: Optional[str] = None


@dataclass
class NovitaAIConfig:
    """Novita AI configuration settings."""

    api_key: str
    base_url: str = "https://api.novita.ai"
    default_model: str = "meta-llama/llama-3.1-70b-instruct"
    translation_model: str = "meta-llama/llama-3.2-3b-instruct"
    timeout: int = 30


@dataclass
class InfluxDBConfig:
    """InfluxDB configuration settings."""

    url: str
    token: str
    org: str
    bucket: str
    timeout: int = 6000

    @classmethod
    def from_env(cls) -> "InfluxDBConfig":
        """Create config from environment with Docker defaults."""
        return cls(
            url=os.getenv("INFLUXDB_URL", "http://localhost:8086"),
            token=os.getenv("INFLUXDB_TOKEN", "my-super-secret-auth-token"),
            org=os.getenv("INFLUXDB_ORG", "webcammerplus"),
            bucket=os.getenv("INFLUXDB_BUCKET", "webcammerplus"),
        )


@dataclass
class AppConfig:
    """Application configuration settings."""

    secret_key: str
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 5000
    cors_origins: list = field(default_factory=lambda: ["*"])
    log_level: str = "INFO"

    # Feature flags
    enable_websocket: bool = True
    enable_metrics: bool = True

    # Rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000


class Config:
    """Central configuration management."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        self._load_from_env()
        self._validate()

    def _load_from_env(self):
        """Load configuration from environment variables."""
        # App configuration
        self.app = AppConfig(
            secret_key=os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"),
            debug=os.getenv("FLASK_DEBUG", "").lower() in ("true", "1", "yes"),
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "5000")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

        # Auth0 configuration
        self.auth0 = Auth0Config(
            domain=os.getenv("AUTH0_DOMAIN", ""),
            client_id=os.getenv("AUTH0_CLIENT_ID", ""),
            client_secret=os.getenv("AUTH0_CLIENT_SECRET", ""),
            audience=os.getenv("AUTH0_AUDIENCE", ""),
        )

        # Stripe configuration
        self.stripe = StripeConfig(
            secret_key=os.getenv("STRIPE_SECRET_KEY", ""),
            webhook_secret=os.getenv("STRIPE_WEBHOOK_SECRET", ""),
            publishable_key=os.getenv("STRIPE_PUBLISHABLE_KEY", ""),
        )

        # Novita AI configuration
        self.novita = NovitaAIConfig(api_key=os.getenv("NOVITA_API_KEY", ""))

        # InfluxDB configuration
        self.influxdb = InfluxDBConfig.from_env()

        # Additional settings
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.is_production = self.environment == "production"

    def _validate(self):
        """Validate required configuration."""
        errors = []

        # Validate Auth0 config
        if not self.auth0.domain:
            errors.append("AUTH0_DOMAIN is required")
        if not self.auth0.client_id:
            errors.append("AUTH0_CLIENT_ID is required")
        if not self.auth0.audience:
            errors.append("AUTH0_AUDIENCE is required")

        # Validate Stripe config
        if not self.stripe.secret_key:
            errors.append("STRIPE_SECRET_KEY is required")
        if not self.stripe.webhook_secret:
            errors.append("STRIPE_WEBHOOK_SECRET is required")

        # Validate Novita AI config
        if not self.novita.api_key:
            errors.append("NOVITA_API_KEY is required")

        # Validate production settings
        if self.is_production:
            if self.app.secret_key == "dev-secret-key-change-in-production":
                errors.append("SECRET_KEY must be changed for production")
            if self.app.debug:
                errors.append("Debug mode should be disabled in production")

        if errors:
            error_msg = "Configuration errors:\n" + "\n".join(
                f"  - {e}" for e in errors
            )
            logger.error(error_msg)
            if self.is_production:
                raise ValueError(error_msg)
            else:
                logger.warning("Running with invalid configuration in development mode")

    def get_database_url(self) -> str:
        """Get the database URL (for future database implementation)."""
        return os.getenv("DATABASE_URL", "sqlite:///webcammerplus.db")

    def get_redis_url(self) -> str:
        """Get Redis URL for caching/sessions (for future implementation)."""
        return os.getenv("REDIS_URL", "redis://localhost:6379/0")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding secrets)."""
        return {
            "environment": self.environment,
            "app": {
                "debug": self.app.debug,
                "host": self.app.host,
                "port": self.app.port,
                "log_level": self.app.log_level,
                "cors_origins": self.app.cors_origins,
                "enable_websocket": self.app.enable_websocket,
                "enable_metrics": self.app.enable_metrics,
            },
            "auth0": {
                "domain": self.auth0.domain,
                "audience": self.auth0.audience,
                "issuer": self.auth0.issuer,
            },
            "influxdb": {
                "url": self.influxdb.url,
                "org": self.influxdb.org,
                "bucket": self.influxdb.bucket,
            },
            "features": {
                "websocket_enabled": self.app.enable_websocket,
                "metrics_enabled": self.app.enable_metrics,
            },
        }


# Singleton instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the configuration singleton instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reset_config():
    """Reset configuration (mainly for testing)."""
    global _config
    _config = None
