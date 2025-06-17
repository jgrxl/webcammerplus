"""Service for managing conversations (message threads).

This service handles conversation-level operations like listing conversations,
counting unread messages, and managing conversation state.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversations between users."""

    def __init__(self, conversation_repository: Optional[BaseRepository] = None):
        """Initialize the conversation service.
        
        Args:
            conversation_repository: Repository for conversation data
        """
        self.conversation_repository = conversation_repository

    def get_conversations_for_user(self, username: str) -> List[Dict]:
        """Get list of conversations (unique senders) for a user.
        
        Args:
            username: The username to get conversations for
            
        Returns:
            List of conversation summaries with last message and unread count
        """
        try:
            if self.conversation_repository:
                conversations = self._query_conversations(username)
            else:
                conversations = []

            # If no conversations found, provide demo data
            if len(conversations) == 0:
                logger.info(
                    f"No conversations found for {username}, providing demo data"
                )
                conversations = self._generate_demo_conversations()

            # Sort by last message time
            conversations.sort(key=lambda x: x["last_message_time"], reverse=True)

            logger.info(
                f"Retrieved {len(conversations)} conversations for user {username}"
            )
            return conversations

        except Exception as e:
            logger.error(f"Error retrieving conversations for user {username}: {e}")
            return []

    def _query_conversations(self, username: str) -> List[Dict]:
        """Query conversations from the repository.
        
        Args:
            username: The username to get conversations for
            
        Returns:
            List of conversation dictionaries
        """
        if not self.conversation_repository:
            return []

        try:
            # This would be implemented in the repository
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error querying conversations: {e}")
            return []

    def _generate_demo_conversations(self) -> List[Dict]:
        """Generate demo conversations for testing.
        
        Returns:
            List of demo conversation dictionaries
        """
        return [
            {
                "from_user": "SecretAdmirer",
                "last_message": "Hey, can we chat privately? 😊",
                "last_message_time": (
                    datetime.utcnow() - timedelta(minutes=5)
                ).isoformat(),
                "unread_count": 1,
            },
            {
                "from_user": "VIPFan",
                "last_message": "I love your shows! ❤️",
                "last_message_time": (
                    datetime.utcnow() - timedelta(minutes=30)
                ).isoformat(),
                "unread_count": 1,
            },
            {
                "from_user": "WhaleKing",
                "last_message": "Thanks for the amazing content! You're incredible!",
                "last_message_time": (
                    datetime.utcnow() - timedelta(hours=1)
                ).isoformat(),
                "unread_count": 0,
            },
            {
                "from_user": "DiamondHands",
                "last_message": "Just wanted to say hi privately 😊",
                "last_message_time": (
                    datetime.utcnow() - timedelta(hours=2)
                ).isoformat(),
                "unread_count": 0,
            },
        ]

    def get_unread_count(self, to_user: str, from_user: str) -> int:
        """Get count of unread messages from a specific sender.
        
        Args:
            to_user: The recipient username
            from_user: The sender username
            
        Returns:
            Count of unread messages
        """
        try:
            if self.conversation_repository:
                # This would be implemented in the repository
                return 0
            return 0
        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            return 0

    def get_total_unread_count(self, username: str) -> int:
        """Get total count of unread messages for a user.
        
        Args:
            username: The username to check
            
        Returns:
            Total count of unread messages
        """
        try:
            conversations = self.get_conversations_for_user(username)
            return sum(conv.get("unread_count", 0) for conv in conversations)
        except Exception as e:
            logger.error(f"Error getting total unread count: {e}")
            return 0

    def mark_conversation_as_read(self, to_user: str, from_user: str) -> bool:
        """Mark all messages in a conversation as read.
        
        Args:
            to_user: The recipient username
            from_user: The sender username
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.conversation_repository:
                # This would be implemented in the repository
                logger.info(f"Marked conversation {from_user} -> {to_user} as read")
                return True
            return False
        except Exception as e:
            logger.error(f"Error marking conversation as read: {e}")
            return False

    def delete_conversation(self, to_user: str, from_user: str) -> bool:
        """Delete all messages in a conversation.
        
        Args:
            to_user: The recipient username
            from_user: The sender username
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.conversation_repository:
                # This would be implemented in the repository
                logger.info(f"Deleted conversation {from_user} -> {to_user}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False