import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from influxdb_client.client.exceptions import InfluxDBError

from client.influx_client import InfluxDBClient
from utils.query_builder import AggregateFunction, FluxQueryBuilder

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
class TipperCount:
    """Represents a tipper and their total tokens.

    Attributes:
        username: The tipper's username
        total_tokens: Total tokens tipped
    """

    username: str
    total_tokens: int


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


@dataclass(frozen=True)
class TopTippersResponse:
    """Response model for top tippers data.

    Attributes:
        tippers: List of top tippers sorted by total tokens
        days: Number of days the query covered
        success: Whether the query was successful
        error: Error message if query failed
    """

    tippers: List[TipperCount]
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
            query = (
                FluxQueryBuilder()
                .from_bucket(self.bucket)
                .range(f"-{days}d")
                .measurement(self.MEASUREMENT_NAME)
                .filter("method", "==", self.TIP_METHOD)
                .field(self.TIP_TOKENS_FIELD)
                .aggregate(AggregateFunction.SUM)
                .build()
            )

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
            flux_query = (
                FluxQueryBuilder()
                .from_bucket(self.bucket)
                .range(f"-{days}d")
                .measurement(self.MEASUREMENT_NAME)
                .filter("method", "==", self.CHAT_METHOD)
                .field(self.USERNAME_FIELD)
                .filter("_value", "!=", "")
                .custom("map(fn: (r) => ({ r with user: r._value }))")
                .custom("filter(fn: (r) => exists r.user)")
                .group_by(["user"])
                .aggregate(AggregateFunction.COUNT)
                .sort("_value", desc=True)
                .limit(limit)
                .build()
            )

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

    def get_top_tippers(
        self, days: int = 7, limit: int = DEFAULT_TOP_CHATTERS_LIMIT
    ) -> "TopTippersResponse":
        """Get the top tippers in the last N days by total tokens.

        Args:
            days: Number of days to look back (default: 7, max: 365)
            limit: Maximum number of tippers to return (default: 10, max: 100)

        Returns:
            TopTippersResponse containing sorted list of top tippers

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
            flux_query = (
                FluxQueryBuilder()
                .from_bucket(self.bucket)
                .range(f"-{days}d")
                .measurement(self.MEASUREMENT_NAME)
                .filter("method", "==", self.TIP_METHOD)
                .field(self.TIP_TOKENS_FIELD)
                .filter("_value", ">", 0)  # Fix: Remove quotes to compare with integer
                .custom('filter(fn: (r) => exists r.username and r.username != "")')
                .group_by(["username"])
                .aggregate(AggregateFunction.SUM)
                .sort("_value", desc=True)
                .limit(limit)
                .build()
            )

            logger.debug(f"Executing top tippers query for {days} days, limit {limit}")
            tables = self.query_api.query(query=flux_query, org=self.org)

            tippers: List["TipperCount"] = []
            for table in tables:
                for record in table.records:
                    username = record.values.get("username")
                    total_tokens = record.get_value()

                    if (
                        username
                        and isinstance(total_tokens, (int, float))
                        and total_tokens > 0
                    ):
                        tippers.append(
                            TipperCount(
                                username=str(username).strip(),
                                total_tokens=int(total_tokens),
                            )
                        )

            # Sort by total tokens descending (extra safety)
            tippers.sort(key=lambda x: x.total_tokens, reverse=True)

            logger.info(f"Retrieved {len(tippers)} top tippers over {days} days")
            return TopTippersResponse(tippers=tippers, days=days)

        except ValueError:
            raise  # Re-raise validation errors
        except InfluxDBError as e:
            logger.error(f"InfluxDB query failed for top tippers: {e}")
            return TopTippersResponse(
                tippers=[],
                days=days,
                success=False,
                error=f"Database query failed: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Unexpected error in get_top_tippers: {e}")
            return TopTippersResponse(
                tippers=[],
                days=days,
                success=False,
                error=f"Unexpected error: {str(e)}",
            )

    # Backward compatibility alias
    def get_top_chatter(self, days: int = 7) -> TopChatterResponse:
        """Backward compatibility alias for get_top_chatters."""
        return self.get_top_chatters(days=days)

    def execute_search_query(
        self,
        measurement: str,
        filters: Optional[Dict[str, Any]] = None,
        range_config: Optional[Dict[str, str]] = None,
        fields: Optional[List[str]] = None,
        sort_by: str = "_time",
        sort_desc: bool = True,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Execute a flexible search query on InfluxDB data.
        
        Args:
            measurement: The measurement name to query
            filters: Dictionary of field filters
            range_config: Time range configuration with 'start' and 'stop'
            fields: List of fields to include in results
            sort_by: Field to sort by
            sort_desc: Sort in descending order
            limit: Maximum number of results
            
        Returns:
            Dictionary with success status, data, and count
        """
        try:
            # Build query using QueryBuilder
            builder = FluxQueryBuilder().from_bucket(self.bucket)
            
            # Add time range
            if range_config:
                start = range_config.get("start", "-7d")
                stop = range_config.get("stop", "now()")
                builder = builder.range(start, stop)
            else:
                builder = builder.range("-7d")
            
            # Add measurement filter
            builder = builder.measurement(measurement)
            
            # Add custom filters
            if filters:
                for key, value in filters.items():
                    # Handle complex filter format
                    if isinstance(value, dict) and "operator" in value and "value" in value:
                        op_str = value["operator"]
                        filter_value = value["value"]
                        try:
                            from utils.query_builder import Operator
                            operator = Operator(op_str)
                        except ValueError:
                            operator = op_str
                        builder = builder.filter(key, operator, filter_value)
                    else:
                        # Simple equality filter
                        builder = builder.filter(key, "==", value)
            
            # Add field selection - avoid _value field as it can have mixed types
            if fields:
                # Filter out _value from keep list to avoid schema collision
                safe_fields = [f for f in fields if f != "_value"]
                if safe_fields:
                    builder = builder.keep(safe_fields)
            
            # Add sorting
            builder = builder.sort(sort_by, desc=sort_desc)
            
            # Add limit
            builder = builder.limit(limit)
            
            # Build and execute query
            flux_query = builder.build()
            logger.debug(f"Executing search query: {flux_query}")
            
            tables = self.query_api.query(query=flux_query, org=self.org)
            
            # Process results
            results = []
            for table in tables:
                for record in table.records:
                    result_dict = {}
                    for key, value in record.values.items():
                        # Include non-internal fields and specific internal fields
                        if not key.startswith("_") or key in [
                            "_time", "_value", "_field", "_measurement"
                        ]:
                            # Convert datetime objects to ISO format strings
                            if hasattr(value, 'isoformat'):
                                result_dict[key] = value.isoformat()
                            else:
                                result_dict[key] = value
                    results.append(result_dict)
            
            logger.info(f"Search query returned {len(results)} results")
            return {
                "success": True,
                "data": results,
                "count": len(results),
            }
            
        except Exception as e:
            logger.error(f"Error executing search query: {e}")
            return {
                "success": False,
                "data": [],
                "count": 0,
                "error": str(e),
            }
