import logging
from typing import Optional

import influxdb_client
from influxdb_client.client.query_api import QueryApi
from influxdb_client.client.write_api import WriteApi

from config import get_config

logger = logging.getLogger(__name__)
config = get_config()


class InfluxDBClient:
    """High-performance InfluxDB client with connection pooling and error handling.

    This client provides a robust interface to InfluxDB with automatic connection
    management, comprehensive error handling, and support for both read and write
    operations.

    Environment Variables:
        INFLUXDB_URL: Database URL (default: http://localhost:8086)
        INFLUXDB_TOKEN: Authentication token (required)
        INFLUXDB_ORG: Organization name (required)
        INFLUXDB_BUCKET: Default bucket name (required)

    Raises:
        ValueError: When required environment variables are missing
        ConnectionError: When connection to InfluxDB fails
    """

    def __init__(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
        org: Optional[str] = None,
        bucket: Optional[str] = None,
    ) -> None:
        """Initialize the InfluxDB client.

        Args:
            url: InfluxDB URL (overrides config)
            token: Authentication token (overrides config)
            org: Organization name (overrides config)
            bucket: Bucket name (overrides config)
        """
        self.url = url or config.influxdb.url
        self.token = token or config.influxdb.token
        self.org = org or config.influxdb.org
        self.bucket = bucket or config.influxdb.bucket

        self._validate_config()
        self._client: Optional[influxdb_client.InfluxDBClient] = None
        self._query_api: Optional[QueryApi] = None
        self._write_api: Optional[WriteApi] = None
        self._is_connected = False

        logger.info(f"Initializing InfluxDB client for {self.url}")
        self._initialize_client()

    def _validate_config(self) -> None:
        """Validate that all required configuration is present.

        Raises:
            ValueError: When required configuration is missing
        """
        missing_vars = []
        if not self.token:
            missing_vars.append("INFLUXDB_TOKEN")
        if not self.org:
            missing_vars.append("INFLUXDB_ORG")
        if not self.bucket:
            missing_vars.append("INFLUXDB_BUCKET")

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

    def _initialize_client(self) -> None:
        """Initialize the InfluxDB client and APIs.

        Raises:
            ConnectionError: When connection initialization fails
        """
        try:
            self._client = influxdb_client.InfluxDBClient(
                url=self.url,
                token=self.token,
                org=self.org,
                enable_gzip=True,
                timeout=10000,  # 10 second timeout
            )

            # Test connection
            health = self._client.health()
            if health.status != "pass":
                raise ConnectionError(f"InfluxDB health check failed: {health.message}")

            self._query_api = self._client.query_api()
            self._write_api = self._client.write_api()
            self._is_connected = True

            logger.info(f"Successfully connected to InfluxDB at {self.url}")

        except Exception as e:
            logger.error(f"Failed to initialize InfluxDB client: {e}")
            self._cleanup_resources()
            raise ConnectionError(f"Failed to connect to InfluxDB: {str(e)}")

    @property
    def client(self) -> influxdb_client.InfluxDBClient:
        """Get the InfluxDB client instance.

        Returns:
            The underlying InfluxDB client

        Raises:
            RuntimeError: When client is not initialized
        """
        if not self._is_connected or self._client is None:
            raise RuntimeError("InfluxDB client not initialized or disconnected")
        return self._client

    @property
    def query_api(self) -> QueryApi:
        """Get the InfluxDB query API instance.

        Returns:
            The query API for read operations

        Raises:
            RuntimeError: When query API is not initialized
        """
        if not self._is_connected or self._query_api is None:
            raise RuntimeError("InfluxDB query API not initialized")
        return self._query_api

    @property
    def write_api(self) -> WriteApi:
        """Get the InfluxDB write API instance.

        Returns:
            The write API for write operations

        Raises:
            RuntimeError: When write API is not initialized
        """
        if not self._is_connected or self._write_api is None:
            raise RuntimeError("InfluxDB write API not initialized")
        return self._write_api

    @property
    def is_connected(self) -> bool:
        """Check if the client is connected to InfluxDB.

        Returns:
            True if connected, False otherwise
        """
        return self._is_connected and self._client is not None

    def _cleanup_resources(self) -> None:
        """Clean up client resources."""
        self._is_connected = False
        if self._client is not None:
            try:
                self._client.close()
            except Exception as e:
                logger.warning(f"Error closing InfluxDB client: {e}")
        self._client = None
        self._query_api = None
        self._write_api = None

    def close(self) -> None:
        """Close the InfluxDB client connection and clean up resources."""
        logger.info("Closing InfluxDB client connection")
        self._cleanup_resources()

    def __enter__(self) -> "InfluxDBClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit with automatic cleanup."""
        self.close()
