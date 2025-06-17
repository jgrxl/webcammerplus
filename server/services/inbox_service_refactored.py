"""Refactored inbox service using specialized services.

This is a cleaner version of the inbox service that delegates to
MessageService and ConversationService for better separation of concerns.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from services.message_service import MessageService
from services.conversation_service import ConversationService

logger = logging.getLogger(__name__)


class InboxServiceRefactored:
    """Refactored facade service for inbox functionality."""

    def __init__(
        self,
        message_service: Optional[MessageService] = None,
        conversation_service: Optional[ConversationService] = None,
    ):
        """Initialize the inbox service.
        
        Args:
            message_service: Service for message operations
            conversation_service: Service for conversation operations
        """
        self.message_service = message_service or MessageService()
        self.conversation_service = conversation_service or ConversationService()

    def get_user_messages(
        self,
        username: str,
        limit: int = 50,
        offset: int = 0,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict]:
        """Get private messages for a specific user.

        Args:
            username: The username to get messages for
            limit: Maximum number of messages to return
            offset: Number of messages to skip
            start_time: Start time for message filtering
            end_time: End time for message filtering

        Returns:
            List of message dictionaries
        """
        return self.message_service.get_messages_for_user(
            username, limit, offset, start_time, end_time
        )

    def get_conversations(self, username: str) -> List[Dict]:
        """Get list of conversations for a user.

        Args:
            username: The username to get conversations for

        Returns:
            List of conversation summaries
        """
        return self.conversation_service.get_conversations_for_user(username)

    def get_unread_count(self, to_user: str, from_user: str) -> int:
        """Get count of unread messages from a specific sender.

        Args:
            to_user: The recipient username
            from_user: The sender username

        Returns:
            Count of unread messages
        """
        return self.conversation_service.get_unread_count(to_user, from_user)

    def get_total_unread_count(self, username: str) -> int:
        """Get total count of all unread messages for a user.

        Args:
            username: The username to check

        Returns:
            Total unread message count
        """
        return self.conversation_service.get_total_unread_count(username)

    def mark_message_as_read(self, message_id: str) -> bool:
        """Mark a message as read.

        Args:
            message_id: The message identifier

        Returns:
            True if successful, False otherwise
        """
        return self.message_service.mark_message_as_read(message_id)

    def mark_conversation_as_read(self, to_user: str, from_user: str) -> bool:
        """Mark all messages in a conversation as read.

        Args:
            to_user: The recipient username
            from_user: The sender username

        Returns:
            True if successful, False otherwise
        """
        return self.conversation_service.mark_conversation_as_read(to_user, from_user)

    def delete_message(self, message_id: str) -> bool:
        """Delete a message.

        Args:
            message_id: The message identifier

        Returns:
            True if successful, False otherwise
        """
        return self.message_service.delete_message(message_id)

    def delete_conversation(self, to_user: str, from_user: str) -> bool:
        """Delete all messages in a conversation.

        Args:
            to_user: The recipient username
            from_user: The sender username

        Returns:
            True if successful, False otherwise
        """
        return self.conversation_service.delete_conversation(to_user, from_user)

    def get_message_count(self, username: str) -> Dict[str, int]:
        """Get message statistics for a user.

        Args:
            username: The username to get stats for

        Returns:
            Dictionary with message counts
        """
        conversations = self.get_conversations(username)
        total_conversations = len(conversations)
        total_unread = self.get_total_unread_count(username)
        
        return {
            "total_conversations": total_conversations,
            "total_unread_messages": total_unread,
            "conversations_with_unread": sum(
                1 for conv in conversations if conv.get("unread_count", 0) > 0
            ),
        }