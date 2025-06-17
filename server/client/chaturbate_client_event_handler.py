import logging
from abc import ABC, abstractmethod
from typing import Dict, Union

try:
    from chaturbate_poller.models import Event, Message, Tip, User
except ImportError:
    # Use mock models for demo mode
    from client.models import Event, Message, Tip, User


logger = logging.getLogger(__name__)


class BaseEventHandler(ABC):
    """Abstract base class for Chaturbate event handlers.

    This provides a contract for implementing custom event handlers
    with consistent interface and error handling.
    """

    @abstractmethod
    async def handle_tip(self, event: Tip) -> None:
        """Handle tip events."""

    @abstractmethod
    async def handle_chat(self, event: Message) -> None:
        """Handle chat message events."""

    @abstractmethod
    async def handle_message(self, event: Event) -> None:
        """Handle generic message events."""


class ChaturbateClientEventHandler(BaseEventHandler):
    """Production-ready event handler for Chaturbate client events.

    This handler processes various types of events from Chaturbate streams
    with comprehensive logging, error handling, and extensible architecture.

    Attributes:
        event_stats: Dictionary tracking event counts by type
        enable_logging: Whether to log events (default: True)
    """

    def __init__(self, enable_logging: bool = True) -> None:
        """Initialize the event handler.

        Args:
            enable_logging: Whether to enable event logging
        """
        self.event_stats: Dict[str, int] = {
            "tips": 0,
            "chat_messages": 0,
            "private_messages": 0,
            "media_purchases": 0,
            "user_events": 0,
            "errors": 0,
        }
        self.enable_logging = enable_logging

        logger.info("Initialized Chaturbate event handler")

    async def handle_tip(self, event: Tip) -> None:
        """Process tip events with comprehensive validation and logging.

        Args:
            event: The tip event to process

        Raises:
            ValueError: If event data is invalid
        """
        try:
            if not event or not event.object or not event.object.user:
                raise ValueError("Invalid tip event: missing required data")

            username = event.object.user.username or "Anonymous"
            amount = event.object.tip.tokens if event.object.tip else 0

            if amount <= 0:
                logger.warning(f"Received invalid tip amount {amount} from {username}")
                return

            self.event_stats["tips"] += 1

            if self.enable_logging:
                logger.info(f"💰 Tip received: {amount} tokens from '{username}'")

            # Process tip based on amount tiers
            await self._process_tip_amount(username, amount)

        except Exception as e:
            self.event_stats["errors"] += 1
            logger.error(f"Error processing tip event: {e}")
            raise

    async def _process_tip_amount(self, username: str, amount: int) -> None:
        """Process tip based on amount with tier-based logic.

        Args:
            username: The tipper's username
            amount: The tip amount in tokens
        """
        if amount >= 1000:
            logger.info(f"🎉 MEGA TIP: {amount} tokens from {username}!")
            # Trigger special mega tip actions
        elif amount >= 100:
            logger.info(f"🔥 Big tip: {amount} tokens from {username}!")
            # Trigger big tip actions
        elif amount >= 25:
            logger.info(f"⭐ Nice tip: {amount} tokens from {username}")
            # Trigger nice tip actions

        # Additional custom logic can be added here

    async def handle_chat(self, event: Message) -> None:
        """Process chat message events with filtering and moderation.

        Args:
            event: The chat message event to process
        """
        try:
            if not event or not event.object or not event.object.user:
                logger.warning("Received invalid chat message event")
                return

            username = event.object.user.username or "Anonymous"
            message = event.object.message or ""

            if not message.strip():
                return  # Ignore empty messages

            self.event_stats["chat_messages"] += 1

            # Basic message filtering
            if await self._is_spam_message(message):
                logger.debug(f"Filtered spam message from {username}")
                return

            if self.enable_logging:
                logger.debug(
                    f"💬 Chat: {username}: {message[:100]}{'...' if len(message) > 100 else ''}"
                )

            # Process message based on content
            await self._process_chat_message(username, message)

        except Exception as e:
            self.event_stats["errors"] += 1
            logger.error(f"Error processing chat message: {e}")

    async def _is_spam_message(self, message: str) -> bool:
        """Check if a message appears to be spam.

        Args:
            message: The message content to check

        Returns:
            True if message appears to be spam
        """
        # Basic spam detection logic
        spam_indicators = [
            len(message) > 500,  # Very long messages
            message.count("http") > 2,  # Multiple URLs
            len(set(message.lower().split()))
            < len(message.split()) * 0.3,  # Too repetitive
        ]
        return any(spam_indicators)

    async def _process_chat_message(self, username: str, message: str) -> None:
        """Process chat message with custom logic.

        Args:
            username: The sender's username
            message: The message content
        """
        # Check for commands or special messages
        if message.startswith("!"):
            await self._handle_command(username, message)
        elif any(word in message.lower() for word in ["hello", "hi", "hey"]):
            logger.debug(f"Greeting detected from {username}")
            # Handle greetings

    async def _handle_command(self, username: str, command: str) -> None:
        """Handle chat commands.

        Args:
            username: The user who sent the command
            command: The command string
        """
        logger.debug(f"Command received from {username}: {command}")
        # Implement command handling logic here

    async def handle_message(self, event: Event) -> None:
        """Process generic message events with type detection.

        Args:
            event: The event to process
        """
        try:
            if not event:
                logger.warning("Received null event")
                return

            # Route event based on type
            if is_chat_message(event):
                await self.handle_chat(event)
            elif is_private_message(event):
                await self.handle_private_message(event)
            else:
                logger.debug(f"Unhandled message event type: {type(event)}")

        except Exception as e:
            self.event_stats["errors"] += 1
            logger.error(f"Error processing message event: {e}")

    async def handle_private_message(self, event: Message) -> None:
        """Process private message events with privacy considerations.

        Args:
            event: The private message event to process
        """
        try:
            if not event or not event.object or not event.object.user:
                logger.warning("Received invalid private message event")
                return

            username = event.object.user.username or "Anonymous"
            message = event.object.message or ""

            if not message.strip():
                return

            self.event_stats["private_messages"] += 1

            # Log private messages with privacy protection
            if self.enable_logging:
                logger.info(
                    f"📧 Private message from '{username}' (length: {len(message)})"
                )

            # Process private message
            await self._process_private_message(username, message)

        except Exception as e:
            self.event_stats["errors"] += 1
            logger.error(f"Error processing private message: {e}")

    async def _process_private_message(self, username: str, message: str) -> None:
        """Process private message with custom logic.

        Args:
            username: The sender's username
            message: The message content (handle with care for privacy)
        """
        # Implement private message handling logic
        # Note: Be careful with logging/storing private message content
        logger.debug(f"Processing private message from {username}")

    async def handle_media_purchase(self, event: Event) -> None:
        """Process media purchase events.

        Args:
            event: The media purchase event to process
        """
        try:
            if not event or not event.object or not event.object.user:
                logger.warning("Received invalid media purchase event")
                return

            username = event.object.user.username or "Anonymous"

            if not hasattr(event.object, "media") or not event.object.media:
                logger.warning(
                    f"Media purchase event from {username} missing media data"
                )
                return

            media = event.object.media
            media_name = getattr(media, "name", "Unknown")
            tokens = getattr(media, "tokens", 0)

            self.event_stats["media_purchases"] += 1

            if self.enable_logging:
                logger.info(
                    f"🎬 Media purchase: '{media_name}' by {username} for {tokens} tokens"
                )

            # Process media purchase
            await self._process_media_purchase(username, media_name, tokens)

        except Exception as e:
            self.event_stats["errors"] += 1
            logger.error(f"Error processing media purchase event: {e}")

    async def _process_media_purchase(
        self, username: str, media_name: str, tokens: int
    ) -> None:
        """Process media purchase with custom logic.

        Args:
            username: The purchaser's username
            media_name: Name of the purchased media
            tokens: Cost in tokens
        """
        logger.debug(
            f"Processing media purchase: {media_name} by {username} for {tokens} tokens"
        )

    async def handle_user(self, user: User) -> None:
        """Process user-related events like joins, follows, etc.

        Args:
            user: The user object
        """
        try:
            if not user or not user.username:
                logger.warning("Received invalid user event")
                return

            username = user.username
            self.event_stats["user_events"] += 1

            if self.enable_logging:
                logger.info(f"👤 User event: {username}")

            # Process user event
            await self._process_user_event(user)

        except Exception as e:
            self.event_stats["errors"] += 1
            logger.error(f"Error processing user event: {e}")

    async def _process_user_event(self, user: User) -> None:
        """Process user event with custom logic.

        Args:
            user: The user object
        """
        # Implement user event handling logic
        logger.debug(f"Processing user event for {user.username}")

    def get_stats(self) -> Dict[str, int]:
        """Get event processing statistics.

        Returns:
            Dictionary of event counts by type
        """
        return self.event_stats.copy()

    def reset_stats(self) -> None:
        """Reset event statistics counters."""
        for key in self.event_stats:
            self.event_stats[key] = 0
        logger.info("Event statistics reset")


def is_private_message(event: Union[Event, Message]) -> bool:
    """Determine if the event represents a private message.

    Args:
        event: The event or message to check

    Returns:
        True if this is a private message, False otherwise
    """
    try:
        if isinstance(event, Message):
            return (
                hasattr(event, "from_user")
                and event.from_user is not None
                and hasattr(event, "to_user")
                and event.to_user is not None
            )
        elif hasattr(event, "object") and hasattr(event.object, "from_user"):
            return (
                event.object.from_user is not None
                and hasattr(event.object, "to_user")
                and event.object.to_user is not None
            )
        return False
    except Exception:
        return False


def is_chat_message(event: Union[Event, Message]) -> bool:
    """Determine if the event represents a public chat message.

    Args:
        event: The event or message to check

    Returns:
        True if this is a public chat message, False otherwise
    """
    try:
        if isinstance(event, Message):
            # Public chat messages typically don't have private routing
            return not is_private_message(event)
        elif hasattr(event, "object") and hasattr(event.object, "message"):
            return not is_private_message(event)
        return False
    except Exception:
        return False


# Backward compatibility alias
ChaturbateClientHandle = ChaturbateClientEventHandler
