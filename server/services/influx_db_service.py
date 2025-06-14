import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List, Union

from client.influx_client import InfluxDBClient
from influxdb_client.client.exceptions import InfluxDBError
from utils.query_builder import FluxQueryBuilder, AggregateFunction


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TipsResponse:
    """Response model for tips data.

    Attributes:
        total_tokens: Total number of tokens received
        days: Number of days the query covered
        success: Whether the query was successful
        error: Error message if query failed
    """

    total_tokens: int
    days: int
    success: bool = True
    error: Optional[str] = None


@dataclass(frozen=True)
class ChatterCount:
    """Represents a chatter and their message count.

    Attributes:
        username: The chatter's username
        count: Number of messages sent
    """

    username: str
    count: int


@dataclass(frozen=True)
class TopChatterResponse:
    """Response model for top chatter data.

    Attributes:
        chatters: List of top chatters sorted by message count
        days: Number of days the query covered
        success: Whether the query was successful
        error: Error message if query failed
    """

    chatters: List[ChatterCount]
    days: int
    success: bool = True
    error: Optional[str] = None


class InfluxDBService:
    """High-level service for Chaturbate analytics using InfluxDB.

    This service provides methods to query Chaturbate event data stored in InfluxDB,
    with built-in error handling, logging, and data validation.

    Attributes:
        client: InfluxDB client instance
        bucket: InfluxDB bucket name
        org: InfluxDB organization name
    """

    # Query constants for better maintainability
    MEASUREMENT_NAME = "chaturbate_events"
    TIP_METHOD = "tip"
    CHAT_METHOD = "chatMessage"
    TIP_TOKENS_FIELD = "object.tip.tokens"
    USERNAME_FIELD = "object.user.username"
    MAX_DAYS_LOOKBACK = 365
    DEFAULT_TOP_CHATTERS_LIMIT = 10

    def __init__(self, client: InfluxDBClient, bucket: str) -> None:
        """Initialize the InfluxDB service.

        Args:
            client: Connected InfluxDB client
            bucket: Target bucket name

        Raises:
            ValueError: If client is not connected or bucket is empty
        """
        if not client.is_connected:
            raise ValueError("InfluxDB client must be connected")
        if not bucket.strip():
            raise ValueError("Bucket name cannot be empty")

        self.client = client
        self.bucket = bucket.strip()
        self.org = client.org
        self.query_api = client.query_api

        logger.info(f"Initialized InfluxDB service for bucket '{self.bucket}'")

    def _validate_days_parameter(self, days: int) -> None:
        """Validate the days parameter.

        Args:
            days: Number of days to validate

        Raises:
            ValueError: If days is invalid
        """
        if not isinstance(days, int):
            raise ValueError(f"Days must be an integer, got {type(days).__name__}")
        if days <= 0:
            raise ValueError(f"Days must be positive, got {days}")
        if days > self.MAX_DAYS_LOOKBACK:
            raise ValueError(f"Days cannot exceed {self.MAX_DAYS_LOOKBACK}, got {days}")

    def get_total_tips(self, days: int = 7) -> TipsResponse:
        """Get total tips received in the last N days.

        Args:
            days: Number of days to look back (default: 7, max: 365)

        Returns:
            TipsResponse containing the sum of tips and metadata

        Raises:
            ValueError: If days parameter is invalid
        """
        try:
            self._validate_days_parameter(days)

            # Build query using QueryBuilder
            query = (FluxQueryBuilder()
                    .from_bucket(self.bucket)
                    .range(f"-{days}d")
                    .measurement(self.MEASUREMENT_NAME)
                    .filter("method", "==", self.TIP_METHOD)
                    .field(self.TIP_TOKENS_FIELD)
                    .aggregate(AggregateFunction.SUM)
                    .build())

            logger.debug(f"Executing tips query for {days} days")
            tables = self.query_api.query(query=query, org=self.org)

            total = 0
            for table in tables:
                for record in table.records:
                    value = record.values.get("_value")
                    if isinstance(value, (int, float)) and value > 0:
                        total += int(value)

            logger.info(f"Retrieved {total} total tokens over {days} days")
            return TipsResponse(total_tokens=total, days=days)

        except ValueError:
            raise  # Re-raise validation errors
        except InfluxDBError as e:
            logger.error(f"InfluxDB query failed for tips: {e}")
            return TipsResponse(
                total_tokens=0,
                days=days,
                success=False,
                error=f"Database query failed: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Unexpected error in get_total_tips: {e}")
            return TipsResponse(
                total_tokens=0,
                days=days,
                success=False,
                error=f"Unexpected error: {str(e)}",
            )

    def get_top_chatters(
        self, days: int = 7, limit: int = DEFAULT_TOP_CHATTERS_LIMIT
    ) -> TopChatterResponse:
        """Get the top chatters in the last N days by message count.

        Args:
            days: Number of days to look back (default: 7, max: 365)
            limit: Maximum number of chatters to return (default: 10, max: 100)

        Returns:
            TopChatterResponse containing sorted list of top chatters

        Raises:
            ValueError: If parameters are invalid
        """
        try:
            self._validate_days_parameter(days)

            if not isinstance(limit, int) or limit <= 0:
                raise ValueError(f"Limit must be a positive integer, got {limit}")
            if limit > 100:
                raise ValueError(f"Limit cannot exceed 100, got {limit}")

            # Build query using QueryBuilder
            flux_query = (FluxQueryBuilder()
                         .from_bucket(self.bucket)
                         .range(f"-{days}d")
                         .measurement(self.MEASUREMENT_NAME)
                         .filter("method", "==", self.CHAT_METHOD)
                         .field(self.USERNAME_FIELD)
                         .filter("_value", "!=", "")
                         .filter("_value", "!=", None)
                         .custom('map(fn: (r) => ({ r with user: r._value }))')
                         .group_by(["user"])
                         .aggregate(AggregateFunction.COUNT)
                         .sort("_value", desc=True)
                         .limit(limit)
                         .build())

            logger.debug(f"Executing top chatters query for {days} days, limit {limit}")
            tables = self.query_api.query(query=flux_query, org=self.org)

            chatters: List[ChatterCount] = []
            for table in tables:
                for record in table.records:
                    username = record.values.get("user")
                    count_value = record.get_value()

                    if (
                        username
                        and isinstance(count_value, (int, float))
                        and count_value > 0
                    ):
                        chatters.append(
                            ChatterCount(
                                username=str(username).strip(), count=int(count_value)
                            )
                        )

            # Sort by count descending (extra safety)
            chatters.sort(key=lambda x: x.count, reverse=True)

            logger.info(f"Retrieved {len(chatters)} top chatters over {days} days")
            return TopChatterResponse(chatters=chatters, days=days)

        except ValueError:
            raise  # Re-raise validation errors
        except InfluxDBError as e:
            logger.error(f"InfluxDB query failed for top chatters: {e}")
            return TopChatterResponse(
                chatters=[],
                days=days,
                success=False,
                error=f"Database query failed: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Unexpected error in get_top_chatters: {e}")
            return TopChatterResponse(
                chatters=[],
                days=days,
                success=False,
                error=f"Unexpected error: {str(e)}",
            )

    # Backward compatibility alias
    def get_top_chatter(self, days: int = 7) -> TopChatterResponse:
        """Backward compatibility alias for get_top_chatters."""
        return self.get_top_chatters(days=days)
