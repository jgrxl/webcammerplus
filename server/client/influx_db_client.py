import os
from typing import Optional

import influxdb_client
from influxdb_client.client.query_api import QueryApi


class InfluxDBClient:
    """Client for interacting with InfluxDB."""

    def __init__(self) -> None:
        self.url = os.getenv("INFLUXDB_URL", "http://localhost:8086")
        self.token = os.getenv("INFLUXDB_TOKEN")
        self.org = os.getenv("INFLUXDB_ORG")
        self.bucket = os.getenv("INFLUXDB_BUCKET")

        self._validate_config()
        self._client: Optional[influxdb_client.InfluxDBClient] = None
        self._query_api: Optional[QueryApi] = None
        self._initialize_client()

    def _validate_config(self) -> None:
        """Validate that all required configuration is present."""
        if not all([self.token, self.org, self.bucket]):
            raise ValueError(
                "Missing required environment variables: "
                "INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET"
            )

    def _initialize_client(self) -> None:
        """Initialize the InfluxDB client and query API."""
        try:
            if self.token is None:
                raise ValueError("INFLUXDB_TOKEN is not set")
            if self.org is None:
                raise ValueError("INFLUXDB_ORG is not set")
            if self.bucket is None:
                raise ValueError("INFLUXDB_BUCKET is not set")

            self._client = influxdb_client.InfluxDBClient(
                url=self.url, token=self.token, org=self.org
            )
            self._query_api = self._client.query_api()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to InfluxDB: {str(e)}")

    @property
    def client(self) -> influxdb_client.InfluxDBClient:
        """Get the InfluxDB client instance."""
        if self._client is None:
            raise RuntimeError("InfluxDB client not initialized")
        return self._client

    @property
    def query_api(self) -> influxdb_client.client.query_api.QueryApi:
        """Get the InfluxDB query API instance."""
        if self._query_api is None:
            raise RuntimeError("InfluxDB query API not initialized")
        return self._query_api

    def close(self) -> None:
        """Close the InfluxDB client connection."""
        if self._client is not None:
            self._client.close()
            self._client = None
            self._query_api = None
