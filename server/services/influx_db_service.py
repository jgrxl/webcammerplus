from dataclasses import dataclass

from influxdb_client import InfluxDBClient
from influxdb_client.client.exceptions import InfluxDBError
from typing import Optional


@dataclass
class TipsResponse:
    """Response model for tips data."""

    total_tokens: int
    days: int
    success: bool = True
    error: str | None = None


@dataclass
class ChatterCount:
    username: str
    count: int


@dataclass
class TopChatterResponse:
    chatters: list[ChatterCount]
    days: int
    success: bool
    error: Optional[str] = None


class InfluxDBService:
    """Service for interacting with InfluxDB."""

    def __init__(self, client: InfluxDBClient, bucket: str):
        self.client = client
        self.bucket = bucket
        self.org = client.org
        self.query_api = client.query_api()

    def get_total_tips(self, days: int = 7) -> TipsResponse:
        """
        Get total tips received in the last N days.

        Args:
            days: Number of days to look back (default: 7)

        Returns:
            TipsResponse containing the sum of tips
        """
        query = f"""
            from(bucket: "{self.bucket}")
                |> range(start: -{days}d)
                |> filter(fn: (r) => r._measurement == "chaturbate_events")
                |> filter(fn: (r) => r.method == "tip")
                |> filter(fn: (r) => r._field == "object.tip.tokens")
                |> sum(column: "_value")
        """

        try:
            # now include the org in the query call
            tables = self.query_api.query(query=query, org=self.org)
            total = sum(
                record.values.get("_value", 0)
                for table in tables
                for record in table.records
            )
            return TipsResponse(total_tokens=total, days=days)
        except InfluxDBError as e:
            return TipsResponse(
                total_tokens=0,
                days=days,
                success=False,
                error=f"Failed to execute query: {e}",
            )

    def get_top_chatter(self, days: int = 7) -> TopChatterResponse:
        """
        Get the top 10 chatters in the last N days, returning their username
        and message count.
        """
        flux = f"""
        from(bucket: "{self.bucket}")
          |> range(start: -{days}d)
          |> filter(fn: (r) => r._measurement == "chaturbate_events")
          |> filter(fn: (r) => r.method == "chatMessage")
          |> filter(fn: (r) => r._field == "object.user.username")
          // copy the username string into its own column
          |> map(fn: (r) => ({{ r with user: r._value }}))
          |> group(columns: ["user"])
          |> count()                         // <- count all rows per user-group
          |> sort(columns: ["_value"], desc: true)
          |> limit(n: 10)
        """

        try:
            tables = self.query_api.query(query=flux)
            chatters: list[ChatterCount] = []
            for table in tables:
                for record in table.records:
                    uname = record.values.get("user")
                    cnt = int(record.get_value())
                    chatters.append(ChatterCount(username=uname, count=cnt))

            return TopChatterResponse(chatters=chatters, days=days, success=True)
        except InfluxDBError as e:
            return TopChatterResponse(
                chatters=[],
                days=days,
                success=False,
                error=f"Failed to execute query: {e!s}",
            )
