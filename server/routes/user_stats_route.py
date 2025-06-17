import logging
from typing import Dict

from flask import request
from flask_restx import Namespace, Resource, fields

from client.influx_client import InfluxDBClient
from utils.auth import requires_auth

logger = logging.getLogger(__name__)

api = Namespace("user_stats", description="User statistics and activity operations")

# Define response models for Swagger documentation
user_stats_model = api.model(
    "UserStats",
    {
        "username": fields.String(required=True, description="Username"),
        "last_tip_time": fields.String(description="Last tip timestamp"),
        "total_tips": fields.Integer(description="Total number of tips"),
        "total_tip_amount": fields.Integer(description="Total tokens tipped"),
        "last_message_time": fields.String(description="Last message timestamp"),
        "total_messages": fields.Integer(description="Total number of messages"),
        "user_status": fields.String(
            description="User status (Regular, Premium, etc.)"
        ),
        "first_seen": fields.String(description="First time user was seen"),
        "days_active": fields.Integer(
            description="Number of days user has been active"
        ),
    },
)


class UserStatsService:
    """Service for retrieving user statistics from InfluxDB."""

    def __init__(self):
        """Initialize the user stats service."""
        self.influx_client = InfluxDBClient()

    def get_user_stats(self, username: str, days: int = 30) -> Dict:
        """
        Get comprehensive statistics for a specific user.

        Args:
            username: The username to get stats for
            days: Number of days to look back (default 30)

        Returns:
            Dictionary with user statistics
        """
        try:
            logger.info(f"Getting stats for user {username} over {days} days")

            # Query for tip statistics
            tip_stats = self._get_tip_stats(username, days)

            # Query for message statistics
            message_stats = self._get_message_stats(username, days)

            # Query for user activity timeline
            activity_stats = self._get_activity_stats(username, days)

            # Combine all statistics
            user_stats = {
                "username": username,
                "last_tip_time": tip_stats.get("last_tip_time"),
                "total_tips": tip_stats.get("total_tips", 0),
                "total_tip_amount": tip_stats.get("total_tip_amount", 0),
                "last_message_time": message_stats.get("last_message_time"),
                "total_messages": message_stats.get("total_messages", 0),
                "first_seen": activity_stats.get("first_seen"),
                "days_active": activity_stats.get("days_active", 0),
                "user_status": self._determine_user_status(
                    tip_stats.get("total_tip_amount", 0)
                ),
            }

            logger.info(f"Retrieved stats for {username}: {user_stats}")
            return user_stats

        except Exception as e:
            logger.error(f"Error getting user stats for {username}: {e}")
            return {
                "username": username,
                "last_tip_time": None,
                "total_tips": 0,
                "total_tip_amount": 0,
                "last_message_time": None,
                "total_messages": 0,
                "first_seen": None,
                "days_active": 0,
                "user_status": "Regular",
            }

    def _get_tip_stats(self, username: str, days: int) -> Dict:
        """Get tip-related statistics for a user."""
        try:
            # Query for tip statistics - filter by specific field to avoid type conflicts
            query = f"""
                from(bucket: "{self.influx_client.bucket}")
                    |> range(start: -{days}d)
                    |> filter(fn: (r) => r["_measurement"] == "chaturbate_events")
                    |> filter(fn: (r) => r["method"] == "tip")
                    |> filter(fn: (r) => r["username"] == "{username}")
                    |> filter(fn: (r) => r["_field"] == "object.tip.tokens")
                    |> sort(columns: ["_time"], desc: true)
            """

            result = self.influx_client.query_api.query(
                org=self.influx_client.org, query=query
            )

            tips = []
            total_amount = 0
            for table in result:
                for record in table.records:
                    tip_amount = record.get_value() or 0
                    tips.append({"time": record.get_time(), "amount": tip_amount})
                    total_amount += tip_amount

            return {
                "total_tips": len(tips),
                "total_tip_amount": total_amount,
                "last_tip_time": tips[0]["time"].isoformat() if tips else None,
            }

        except Exception as e:
            logger.error(f"Error getting tip stats for {username}: {e}")
            return {"total_tips": 0, "total_tip_amount": 0, "last_tip_time": None}

    def _get_message_stats(self, username: str, days: int) -> Dict:
        """Get message-related statistics for a user."""
        try:
            # Query for message statistics
            query = f"""
                from(bucket: "{self.influx_client.bucket}")
                    |> range(start: -{days}d)
                    |> filter(fn: (r) => r["_measurement"] == "chaturbate_events")
                    |> filter(fn: (r) => r["method"] == "chatMessage")
                    |> filter(fn: (r) => r["username"] == "{username}")
                    |> filter(fn: (r) => r["_field"] == "object.message")
                    |> sort(columns: ["_time"], desc: true)
            """

            result = self.influx_client.query_api.query(
                org=self.influx_client.org, query=query
            )

            messages = []
            for table in result:
                for record in table.records:
                    messages.append(
                        {"time": record.get_time(), "message": record.get_value()}
                    )

            return {
                "total_messages": len(messages),
                "last_message_time": messages[0]["time"].isoformat()
                if messages
                else None,
            }

        except Exception as e:
            logger.error(f"Error getting message stats for {username}: {e}")
            return {"total_messages": 0, "last_message_time": None}

    def _get_activity_stats(self, username: str, days: int) -> Dict:
        """Get general activity statistics for a user."""
        try:
            times = []

            # Query for tip activity times
            tip_query = f"""
                from(bucket: "{self.influx_client.bucket}")
                    |> range(start: -{days}d)
                    |> filter(fn: (r) => r["_measurement"] == "chaturbate_events")
                    |> filter(fn: (r) => r["username"] == "{username}")
                    |> filter(fn: (r) => r["_field"] == "object.tip.tokens")
                    |> sort(columns: ["_time"], desc: false)
            """

            tip_result = self.influx_client.query_api.query(
                org=self.influx_client.org, query=tip_query
            )

            for table in tip_result:
                for record in table.records:
                    times.append(record.get_time())

            # Query for message activity times
            message_query = f"""
                from(bucket: "{self.influx_client.bucket}")
                    |> range(start: -{days}d)
                    |> filter(fn: (r) => r["_measurement"] == "chaturbate_events")
                    |> filter(fn: (r) => r["username"] == "{username}")
                    |> filter(fn: (r) => r["_field"] == "object.message")
                    |> sort(columns: ["_time"], desc: false)
            """

            message_result = self.influx_client.query_api.query(
                org=self.influx_client.org, query=message_query
            )

            for table in message_result:
                for record in table.records:
                    times.append(record.get_time())

            if not times:
                return {"first_seen": None, "days_active": 0}

            first_seen = min(times)
            last_seen = max(times)
            days_active = (last_seen - first_seen).days + 1

            return {
                "first_seen": first_seen.isoformat(),
                "days_active": days_active,
            }

        except Exception as e:
            logger.error(f"Error getting activity stats for {username}: {e}")
            return {"first_seen": None, "days_active": 0}

    def _determine_user_status(self, total_tip_amount: int) -> str:
        """Determine user status based on tip amount."""
        if total_tip_amount >= 1000:
            return "VIP"
        elif total_tip_amount >= 500:
            return "Premium"
        elif total_tip_amount >= 100:
            return "Supporter"
        elif total_tip_amount > 0:
            return "Tipper"
        else:
            return "Regular"


@api.route("/<string:username>")
class UserStatsResource(Resource):
    @api.doc("get_user_stats")
    @api.marshal_with(user_stats_model)
    @api.param("days", "Number of days to look back", type=int, default=30)
    @requires_auth
    def get(self, username):
        """Get comprehensive statistics for a specific user."""
        try:
            days = request.args.get("days", 30, type=int)

            user_stats_service = UserStatsService()
            stats = user_stats_service.get_user_stats(username, days)

            return stats

        except Exception as e:
            logger.error(f"Error retrieving user stats for {username}: {e}")
            api.abort(500, f"Failed to retrieve user stats: {str(e)}")


@api.route("/bulk")
class BulkUserStatsResource(Resource):
    @api.doc("get_bulk_user_stats")
    @api.expect(
        api.model(
            "UserList",
            {
                "usernames": fields.List(
                    fields.String, required=True, description="List of usernames"
                )
            },
        )
    )
    @api.marshal_list_with(user_stats_model)
    @requires_auth
    def post(self):
        """Get statistics for multiple users at once."""
        try:
            data = request.get_json()
            usernames = data.get("usernames", [])
            days = data.get("days", 30)

            if not usernames:
                api.abort(400, "No usernames provided")

            user_stats_service = UserStatsService()
            stats_list = []

            for username in usernames:
                stats = user_stats_service.get_user_stats(username, days)
                stats_list.append(stats)

            return stats_list

        except Exception as e:
            logger.error(f"Error retrieving bulk user stats: {e}")
            api.abort(500, f"Failed to retrieve bulk user stats: {str(e)}")
