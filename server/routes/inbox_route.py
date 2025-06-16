import logging
from datetime import datetime

from flask import request
from flask_restx import Namespace, Resource, fields
from werkzeug.exceptions import BadRequest, NotFound

from services.inbox_service import InboxService
from utils.auth import requires_auth

logger = logging.getLogger(__name__)

api = Namespace("inbox", description="Private message inbox operations")

# Define response models for Swagger documentation
message_model = api.model(
    "Message",
    {
        "id": fields.String(required=True, description="Message ID"),
        "from_user": fields.String(required=True, description="Sender username"),
        "to_user": fields.String(required=True, description="Recipient username"),
        "message": fields.String(required=True, description="Message content"),
        "timestamp": fields.String(required=True, description="Message timestamp"),
        "is_read": fields.Boolean(required=True, description="Read status"),
        "is_sent": fields.Boolean(description="Whether user sent this message"),
    },
)

conversation_model = api.model(
    "Conversation",
    {
        "from_user": fields.String(
            required=True, description="Other user in conversation"
        ),
        "last_message": fields.String(
            required=True, description="Last message preview"
        ),
        "last_message_time": fields.String(
            required=True, description="Last message timestamp"
        ),
        "unread_count": fields.Integer(
            required=True, description="Number of unread messages"
        ),
    },
)

inbox_stats_model = api.model(
    "InboxStats",
    {
        "total_messages": fields.Integer(required=True, description="Total messages"),
        "unread_messages": fields.Integer(required=True, description="Unread messages"),
        "read_messages": fields.Integer(required=True, description="Read messages"),
    },
)


@api.route("/messages")
class InboxMessages(Resource):
    @api.doc("get_inbox_messages")
    @api.marshal_list_with(message_model)
    @api.param("limit", "Maximum number of messages to return", type=int, default=50)
    @api.param("offset", "Number of messages to skip", type=int, default=0)
    @api.param("start_time", "Start time for filtering (ISO format)", type=str)
    @api.param("end_time", "End time for filtering (ISO format)", type=str)
    @requires_auth
    def get(self):
        """Get user's private messages."""
        try:
            # Get query parameters
            limit = request.args.get("limit", 50, type=int)
            offset = request.args.get("offset", 0, type=int)
            start_time_str = request.args.get("start_time")
            end_time_str = request.args.get("end_time")

            # Parse time parameters
            start_time = None
            end_time = None
            if start_time_str:
                start_time = datetime.fromisoformat(
                    start_time_str.replace("Z", "+00:00")
                )
            if end_time_str:
                end_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))

            # Get messages from service
            user = request.user
            inbox_service = InboxService()
            messages = inbox_service.get_user_messages(
                username=user.auth0_id,
                limit=limit,
                offset=offset,
                start_time=start_time,
                end_time=end_time,
            )

            return messages

        except ValueError as e:
            logger.error(f"Invalid parameter: {e}")
            raise BadRequest(f"Invalid parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Error retrieving inbox messages: {e}")
            api.abort(500, f"Failed to retrieve messages: {str(e)}")


@api.route("/conversations")
class InboxConversations(Resource):
    @api.doc("get_conversations")
    @api.marshal_list_with(conversation_model)
    @requires_auth
    def get(self):
        """Get list of conversations (unique senders with last message)."""
        try:
            user = request.user
            logger.info(f"💬 Getting conversations for user: {user.auth0_id}")
            inbox_service = InboxService()
            conversations = inbox_service.get_conversations(
                username=user.auth0_id
            )
            logger.info(f"💬 Found {len(conversations)} conversations")
            return conversations

        except Exception as e:
            logger.error(f"Error retrieving conversations: {e}")
            api.abort(500, f"Failed to retrieve conversations: {str(e)}")


@api.route("/conversations/<string:other_user>")
class ConversationMessages(Resource):
    @api.doc("get_conversation_messages")
    @api.marshal_list_with(message_model)
    @api.param("limit", "Maximum number of messages to return", type=int, default=50)
    @api.param("offset", "Number of messages to skip", type=int, default=0)
    @requires_auth
    def get(self, other_user):
        """Get all messages in a conversation with a specific user."""
        try:
            user = request.user
            limit = request.args.get("limit", 50, type=int)
            offset = request.args.get("offset", 0, type=int)

            logger.info(f"🔍 Getting conversation messages between {user.auth0_id} and {other_user}")
            logger.info(f"🔍 Query params: limit={limit}, offset={offset}")

            inbox_service = InboxService()
            messages = inbox_service.get_conversation_messages(
                username=user.auth0_id,
                other_user=other_user,
                limit=limit,
                offset=offset,
            )

            logger.info(f"🔍 Retrieved {len(messages)} messages for conversation")
            logger.info(f"🔍 Messages: {messages}")
            return messages

        except Exception as e:
            logger.error(f"Error retrieving conversation messages: {e}")
            api.abort(500, f"Failed to retrieve conversation: {str(e)}")


@api.route("/messages/<string:message_id>/read")
class MarkMessageRead(Resource):
    @api.doc("mark_message_read")
    @requires_auth
    def post(self, message_id):
        """Mark a message as read."""
        try:
            user = request.user
            inbox_service = InboxService()
            success = inbox_service.mark_message_as_read(
                username=user.auth0_id,
                message_id=message_id,
            )

            if success:
                return {"message": "Message marked as read"}, 200
            else:
                raise NotFound("Message not found or already read")

        except NotFound:
            raise
        except Exception as e:
            logger.error(f"Error marking message as read: {e}")
            api.abort(500, f"Failed to mark message as read: {str(e)}")


@api.route("/messages/<string:message_id>")
class DeleteMessage(Resource):
    @api.doc("delete_message")
    @requires_auth
    def delete(self, message_id):
        """Delete a message."""
        try:
            user = request.user
            inbox_service = InboxService()
            success = inbox_service.delete_message(
                username=user.auth0_id,
                message_id=message_id,
            )

            if success:
                return {"message": "Message deleted"}, 200
            else:
                raise NotFound("Message not found")

        except NotFound:
            raise
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            api.abort(500, f"Failed to delete message: {str(e)}")


@api.route("/stats")
class InboxStats(Resource):
    @api.doc("get_inbox_stats")
    @api.marshal_with(inbox_stats_model)
    @requires_auth
    def get(self):
        """Get inbox statistics for the current user."""
        try:
            user = request.user
            logger.info(f"📊 Getting inbox stats for user: {user.auth0_id}")
            logger.info(f"📊 User object: {user}")
            inbox_service = InboxService()
            stats = inbox_service.get_inbox_stats(
                username=user.auth0_id
            )
            logger.info(f"📊 Inbox stats result: {stats}")
            return stats

        except AttributeError as e:
            logger.error(f"User object issue: {e}")
            logger.error(f"Request object: {dir(request)}")
            api.abort(500, f"Authentication issue: {str(e)}")
        except Exception as e:
            logger.error(f"Error retrieving inbox stats: {e}")
            api.abort(500, f"Failed to retrieve inbox stats: {str(e)}")


@api.route("/mark-all-read")
class MarkAllRead(Resource):
    @api.doc("mark_all_read")
    @requires_auth
    def post(self):
        """Mark all messages as read."""
        try:
            user = request.user
            username = user.auth0_id
            inbox_service = InboxService()

            # Get all unread messages
            messages = inbox_service.get_user_messages(username=username, limit=1000)
            unread_messages = [msg for msg in messages if not msg.get("is_read", False)]

            # Mark each as read
            marked_count = 0
            for message in unread_messages:
                if inbox_service.mark_message_as_read(username, message["id"]):
                    marked_count += 1

            return {
                "message": f"Marked {marked_count} messages as read",
                "marked_count": marked_count,
            }, 200

        except Exception as e:
            logger.error(f"Error marking all messages as read: {e}")
            api.abort(500, f"Failed to mark all messages as read: {str(e)}")


@api.route("/test/<string:other_user>")
class InboxTest(Resource):
    @api.doc("test_inbox")
    @requires_auth
    def get(self, other_user):
        """Test inbox functionality - debug endpoint."""
        try:
            user = request.user
            logger.info(f"🧪 TEST: User auth0_id: {user.auth0_id}")
            logger.info(f"🧪 TEST: Other user: {other_user}")
            
            inbox_service = InboxService()
            
            # Test conversations
            conversations = inbox_service.get_conversations(username=user.auth0_id)
            logger.info(f"🧪 TEST: Found {len(conversations)} conversations")
            
            # Test messages for this specific user
            messages = inbox_service.get_conversation_messages(
                username=user.auth0_id,
                other_user=other_user,
                limit=10,
                offset=0,
            )
            logger.info(f"🧪 TEST: Found {len(messages)} messages with {other_user}")
            
            return {
                "user_id": user.auth0_id,
                "other_user": other_user,
                "conversations_count": len(conversations),
                "conversations": conversations[:3],  # First 3 for debugging
                "messages_count": len(messages),
                "messages": messages[:3],  # First 3 for debugging
            }
            
        except Exception as e:
            logger.error(f"🧪 TEST: Error in inbox test: {e}")
            api.abort(500, f"Test failed: {str(e)}")
