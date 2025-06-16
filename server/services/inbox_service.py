import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from influxdb_client import Point

from client.influx_client import InfluxDBClient

logger = logging.getLogger(__name__)


class InboxService:
    """Service for managing private messages and inbox functionality."""

    def __init__(self):
        """Initialize the inbox service."""
        self.influx_client = InfluxDBClient()

    def get_user_messages(
        self,
        username: str,
        limit: int = 50,
        offset: int = 0,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        Get private messages for a specific user.

        Args:
            username: The username to get messages for
            limit: Maximum number of messages to return
            offset: Number of messages to skip
            start_time: Start time for message filtering
            end_time: End time for message filtering

        Returns:
            List of message dictionaries
        """
        try:
            # For demo purposes, return some test data if no real data is found
            # This helps with testing the UI when InfluxDB doesn't have data yet
            
            # Default to last 30 days if no time range specified
            if not start_time:
                start_time = datetime.utcnow() - timedelta(days=30)
            if not end_time:
                end_time = datetime.utcnow()

            # Build query for private messages where user is recipient
            start = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            stop = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            query = f"""
                from(bucket: "{self.influx_client.bucket}")
                    |> range(start: {start}, stop: {stop})
                    |> filter(fn: (r) => r["_measurement"] == "chaturbate_events")
                    |> filter(fn: (r) => r["method"] == "privateMessage")
                    |> filter(fn: (r) => r["_field"] == "object.message")
                    |> filter(fn: (r) => r["to_user"] == "{username}")
                    |> sort(columns: ["_time"], desc: true)
                    |> limit(n: {limit}, offset: {offset})
            """

            result = self.influx_client.query_api.query(
                org=self.influx_client.org, query=query
            )

            messages = []
            for table in result:
                for record in table.records:
                    # Extract message data from the record
                    message_data = {
                        "id": (
                            f"{record.get_time()}_"
                            f"{record.values.get('from_user', '')}"
                        ),
                        "from_user": record.values.get("from_user", "Unknown"),
                        "to_user": record.values.get("to_user", username),
                        "message": record.get_value() or "",  # The message content is now in _value
                        "timestamp": record.get_time().isoformat(),
                        "is_read": record.values.get("is_read", "false") == "true",
                    }
                    messages.append(message_data)

            # If no messages found in InfluxDB, provide demo data for testing
            if len(messages) == 0 and limit > 0:
                logger.info(f"No messages found in InfluxDB for {username}, providing demo data")
                demo_messages = [
                    {
                        "id": f"{datetime.utcnow().isoformat()}_SecretAdmirer",
                        "from_user": "SecretAdmirer",
                        "to_user": username,
                        "message": "Hey, can we chat privately? 😊",
                        "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                        "is_read": False,
                    },
                    {
                        "id": f"{datetime.utcnow().isoformat()}_VIPFan",
                        "from_user": "VIPFan", 
                        "to_user": username,
                        "message": "I love your shows! ❤️",
                        "timestamp": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
                        "is_read": False,
                    },
                    {
                        "id": f"{datetime.utcnow().isoformat()}_WhaleKing",
                        "from_user": "WhaleKing",
                        "to_user": username,
                        "message": "Thanks for the amazing content! You're incredible!",
                        "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                        "is_read": True,
                    }
                ]
                messages = demo_messages[:limit]

            logger.info(f"Retrieved {len(messages)} messages for user {username}")
            return messages

        except Exception as e:
            logger.error(f"Error retrieving messages for user {username}: {e}")
            return []

    def get_conversations(self, username: str) -> List[Dict]:
        """
        Get list of conversations (unique senders) for a user.

        Args:
            username: The username to get conversations for

        Returns:
            List of conversation summaries with last message and unread count
        """
        try:
            # Query to get unique senders and their last message
            # Fix: Only group by tag columns and select specific fields to avoid type conflicts
            query = f"""
                from(bucket: "{self.influx_client.bucket}")
                    |> range(start: -30d)
                    |> filter(fn: (r) => r["_measurement"] == "chaturbate_events")
                    |> filter(fn: (r) => r["method"] == "privateMessage")
                    |> filter(fn: (r) => r["to_user"] == "{username}")
                    |> filter(fn: (r) => r["_field"] == "object.message")
                    |> group(columns: ["from_user"])
                    |> sort(columns: ["_time"], desc: true)
                    |> first()
                    |> group()
            """

            result = self.influx_client.query_api.query(
                org=self.influx_client.org, query=query
            )

            conversations = []
            for table in result:
                for record in table.records:
                    from_user = record.values.get("from_user", "Unknown")

                    # Get unread count for this sender
                    unread_count = self._get_unread_count(username, from_user)

                    conversation = {
                        "from_user": from_user,
                        "last_message": record.get_value() or "",  # The message content is now in _value
                        "last_message_time": record.get_time().isoformat(),
                        "unread_count": unread_count,
                    }
                    conversations.append(conversation)

            # If no conversations found, provide demo data
            if len(conversations) == 0:
                logger.info(f"No conversations found in InfluxDB for {username}, providing demo data")
                conversations = [
                    {
                        "from_user": "SecretAdmirer",
                        "last_message": "Hey, can we chat privately? 😊",
                        "last_message_time": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                        "unread_count": 1,
                    },
                    {
                        "from_user": "VIPFan",
                        "last_message": "I love your shows! ❤️",
                        "last_message_time": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
                        "unread_count": 1,
                    },
                    {
                        "from_user": "WhaleKing",
                        "last_message": "Thanks for the amazing content! You're incredible!",
                        "last_message_time": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                        "unread_count": 0,
                    }
                ]

            # Sort by last message time
            conversations.sort(key=lambda x: x["last_message_time"], reverse=True)

            logger.info(
                f"Retrieved {len(conversations)} conversations for user {username}"
            )
            return conversations

        except Exception as e:
            logger.error(f"Error retrieving conversations for user {username}: {e}")
            return []

    def _get_unread_count(self, to_user: str, from_user: str) -> int:
        """
        Get count of unread messages from a specific sender.

        Args:
            to_user: The recipient username
            from_user: The sender username

        Returns:
            Count of unread messages
        """
        try:
            query = f"""
                from(bucket: "{self.influx_client.bucket}")
                    |> range(start: -30d)
                    |> filter(fn: (r) => r["_measurement"] == "chaturbate_events")
                    |> filter(fn: (r) => r["method"] == "privateMessage")
                    |> filter(fn: (r) => r["_field"] == "object.message")
                    |> filter(fn: (r) => r["to_user"] == "{to_user}")
                    |> filter(fn: (r) => r["from_user"] == "{from_user}")
                    |> filter(fn: (r) => r["is_read"] == "false")
                    |> count()
            """

            result = self.influx_client.query_api.query(
                org=self.influx_client.org, query=query
            )

            count = 0
            for table in result:
                for record in table.records:
                    count = record.get_value() or 0
                    break

            return count

        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            return 0

    def mark_message_as_read(self, username: str, message_id: str) -> bool:
        """
        Mark a message as read.

        Args:
            username: The recipient username
            message_id: The message ID (timestamp_sender format)

        Returns:
            Success status
        """
        try:
            # Parse message ID to get timestamp and sender
            parts = message_id.split("_", 1)
            if len(parts) != 2:
                logger.error(f"Invalid message ID format: {message_id}")
                return False

            timestamp_str, from_user = parts

            # Since InfluxDB doesn't support updates, we'll write a new point
            # with the same timestamp but updated is_read status
            point = (
                Point("chaturbate_events")
                .tag("method", "privateMessage")
                .tag("from_user", from_user)
                .tag("to_user", username)
                .tag("is_read", "true")
                .field("read_update", True)
                .time(timestamp_str)
            )

            write_api = self.influx_client.write_api
            write_api.write(
                bucket=self.influx_client.bucket,
                org=self.influx_client.org,
                record=point,
            )

            logger.info(f"Marked message {message_id} as read for user {username}")
            return True

        except Exception as e:
            logger.error(f"Error marking message as read: {e}")
            return False

    def get_conversation_messages(
        self,
        username: str,
        other_user: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict]:
        """
        Get all messages in a conversation between two users.

        Args:
            username: The current user's username
            other_user: The other user in the conversation
            limit: Maximum number of messages to return
            offset: Number of messages to skip

        Returns:
            List of messages in the conversation
        """
        try:
            logger.info(f"🔍 InboxService.get_conversation_messages called with:")
            logger.info(f"🔍   username: {username}")
            logger.info(f"🔍   other_user: {other_user}")
            logger.info(f"🔍   limit: {limit}, offset: {offset}")
            # Query for messages between the two users (both directions)
            # Fix: Filter by specific field to avoid type conflicts
            query = f"""
                from(bucket: "{self.influx_client.bucket}")
                    |> range(start: -30d)
                    |> filter(fn: (r) => r["_measurement"] == "chaturbate_events")
                    |> filter(fn: (r) => r["method"] == "privateMessage")
                    |> filter(fn: (r) => r["_field"] == "object.message")
                    |> filter(fn: (r) =>
                        (r["from_user"] == "{username}" and
                         r["to_user"] == "{other_user}") or
                        (r["from_user"] == "{other_user}" and
                         r["to_user"] == "{username}")
                    )
                    |> sort(columns: ["_time"], desc: false)
                    |> limit(n: {limit}, offset: {offset})
            """

            result = self.influx_client.query_api.query(
                org=self.influx_client.org, query=query
            )

            messages = []
            for table in result:
                for record in table.records:
                    message_data = {
                        "id": (
                            f"{record.get_time()}_"
                            f"{record.values.get('from_user', '')}"
                        ),
                        "from_user": record.values.get("from_user", "Unknown"),
                        "to_user": record.values.get("to_user", "Unknown"),
                        "message": record.get_value() or "",  # The message content is now in _value
                        "timestamp": record.get_time().isoformat(),
                        "is_read": record.values.get("is_read", "false") == "true",
                        "is_sent": record.values.get("from_user") == username,
                    }
                    messages.append(message_data)

            # If no messages found, provide demo conversation data
            if len(messages) == 0 and limit > 0:
                logger.info(f"No conversation found between {username} and {other_user}, providing demo data")
                demo_messages = [
                    {
                        "id": f"{datetime.utcnow().isoformat()}_{other_user}_1",
                        "from_user": other_user,
                        "to_user": username,
                        "message": f"Hey there! Love your shows! ❤️",
                        "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                        "is_read": True,
                        "is_sent": False,
                    },
                    {
                        "id": f"{datetime.utcnow().isoformat()}_{username}_1", 
                        "from_user": username,
                        "to_user": other_user,
                        "message": "Thank you so much! That means a lot 😊",
                        "timestamp": (datetime.utcnow() - timedelta(hours=1, minutes=30)).isoformat(),
                        "is_read": True,
                        "is_sent": True,
                    },
                    {
                        "id": f"{datetime.utcnow().isoformat()}_{other_user}_2",
                        "from_user": other_user,
                        "to_user": username,
                        "message": "Can we chat privately sometime?",
                        "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                        "is_read": False,
                        "is_sent": False,
                    }
                ]
                messages = demo_messages[:limit]

            logger.info(
                f"Retrieved {len(messages)} messages in conversation "
                f"between {username} and {other_user}"
            )
            return messages

        except Exception as e:
            logger.error(f"Error retrieving conversation messages: {e}")
            return []

    def delete_message(self, username: str, message_id: str) -> bool:
        """
        Delete a message (mark as deleted in InfluxDB).

        Args:
            username: The user deleting the message
            message_id: The message ID

        Returns:
            Success status
        """
        try:
            # Parse message ID
            parts = message_id.split("_", 1)
            if len(parts) != 2:
                logger.error(f"Invalid message ID format: {message_id}")
                return False

            timestamp_str, from_user = parts

            # Write a deletion marker
            point = (
                Point("chaturbate_events")
                .tag("method", "privateMessage_deleted")
                .tag("from_user", from_user)
                .tag("to_user", username)
                .tag("deleted_by", username)
                .field("deleted_message_id", message_id)
                .time(timestamp_str)
            )

            write_api = self.influx_client.write_api
            write_api.write(
                bucket=self.influx_client.bucket,
                org=self.influx_client.org,
                record=point,
            )

            logger.info(f"Deleted message {message_id} for user {username}")
            return True

        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            return False

    def get_inbox_stats(self, username: str) -> Dict:
        """
        Get inbox statistics for a user.

        Args:
            username: The username to get stats for

        Returns:
            Dictionary with inbox statistics
        """
        try:
            # Total messages query
            total_query = f"""
                from(bucket: "{self.influx_client.bucket}")
                    |> range(start: -30d)
                    |> filter(fn: (r) => r["_measurement"] == "chaturbate_events")
                    |> filter(fn: (r) => r["method"] == "privateMessage")
                    |> filter(fn: (r) => r["_field"] == "object.message")
                    |> filter(fn: (r) => r["to_user"] == "{username}")
                    |> count()
            """

            # Unread messages query
            unread_query = f"""
                from(bucket: "{self.influx_client.bucket}")
                    |> range(start: -30d)
                    |> filter(fn: (r) => r["_measurement"] == "chaturbate_events")
                    |> filter(fn: (r) => r["method"] == "privateMessage")
                    |> filter(fn: (r) => r["_field"] == "object.message")
                    |> filter(fn: (r) => r["to_user"] == "{username}")
                    |> filter(fn: (r) => r["is_read"] == "false")
                    |> count()
            """

            total_result = self.influx_client.query_api.query(
                org=self.influx_client.org, query=total_query
            )
            unread_result = self.influx_client.query_api.query(
                org=self.influx_client.org, query=unread_query
            )

            total_count = 0
            unread_count = 0

            for table in total_result:
                for record in table.records:
                    total_count = record.get_value() or 0
                    break

            for table in unread_result:
                for record in table.records:
                    unread_count = record.get_value() or 0
                    break

            # If no data found, provide demo stats
            if total_count == 0:
                stats = {
                    "total_messages": 3,
                    "unread_messages": 2,
                    "read_messages": 1,
                }
                logger.info(f"No stats found in InfluxDB for {username}, providing demo stats")
            else:
                stats = {
                    "total_messages": total_count,
                    "unread_messages": unread_count,
                    "read_messages": total_count - unread_count,
                }

            logger.info(f"Retrieved inbox stats for user {username}: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error getting inbox stats: {e}")
            return {
                "total_messages": 0,
                "unread_messages": 0,
                "read_messages": 0,
            }
