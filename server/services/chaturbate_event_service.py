import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from influxdb_client import Point
from flask_socketio import SocketIO

from models.events import (
    BaseEvent, EventType, TipEvent, MessageEvent, 
    PrivateMessageEvent, UserJoinEvent, UserLeaveEvent,
    MediaPurchaseEvent, User
)
from repositories.event_repository import EventRepository

logger = logging.getLogger(__name__)


class EventProcessingService:
    """Service for processing Chaturbate events with InfluxDB storage and WebSocket broadcasting."""
    
    def __init__(self, event_repository: Optional[EventRepository] = None, socketio: Optional[SocketIO] = None):
        self.event_handlers: Dict[EventType, List[Callable]] = {
            event_type: [] for event_type in EventType
        }
        self.global_handlers: List[Callable] = []
        self.event_repository = event_repository
        self.socketio = socketio
        self._stats = {
            "tips_processed": 0,
            "messages_processed": 0,
            "private_messages_processed": 0,
            "errors": 0
        }
    
    def register_handler(self, event_type: EventType, handler: Callable) -> None:
        """Register a handler for a specific event type.
        
        Args:
            event_type: The type of event to handle
            handler: Callable that takes an event and processes it
        """
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for {event_type.value} events")
    
    def register_global_handler(self, handler: Callable) -> None:
        """Register a handler that processes all events.
        
        Args:
            handler: Callable that takes any event and processes it
        """
        self.global_handlers.append(handler)
        logger.info("Registered global event handler")
    
    def set_socketio(self, socketio: SocketIO) -> None:
        """Set the SocketIO instance for WebSocket broadcasting.
        
        Args:
            socketio: The SocketIO instance
        """
        self.socketio = socketio
        logger.info("SocketIO instance set for EventProcessingService")
    
    def set_event_repository(self, repository: EventRepository) -> None:
        """Set the event repository for data persistence.
        
        Args:
            repository: The EventRepository instance
        """
        self.event_repository = repository
        logger.info("EventRepository set for EventProcessingService")
    
    async def process_and_store_event(self, event: Any, event_type: str) -> Dict[str, Any]:
        """Process an event, store it in InfluxDB, and broadcast via WebSocket.
        
        Args:
            event: The event object (from chaturbate_poller or mock)
            event_type: The type of event (tip, chat, private_message)
            
        Returns:
            Processed event data dictionary
        """
        try:
            # Extract common fields
            timestamp = getattr(event, 'timestamp', datetime.utcnow())
            
            # Process based on event type
            if event_type == "tip":
                return await self._process_tip_event(event, timestamp)
            elif event_type == "chat":
                return await self._process_chat_event(event, timestamp)
            elif event_type == "private_message":
                return await self._process_private_message_event(event, timestamp)
            else:
                logger.warning(f"Unknown event type: {event_type}")
                return {}
                
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Error processing event: {e}")
            return {}
    
    async def _process_tip_event(self, event: Any, timestamp: datetime) -> Dict[str, Any]:
        """Process a tip event."""
        username = event.object.user.username if event.object and event.object.user else "Anonymous"
        amount = event.object.tip.tokens if event.object and event.object.tip else 0
        message = getattr(event.object.tip, "message", "") if event.object and event.object.tip else ""
        
        # Store in InfluxDB
        if self.event_repository:
            point = (
                Point("chaturbate_events")
                .tag("method", "tip")
                .tag("username", username)
                .field("object.tip.tokens", amount)
                .field("object.user.username", username)
                .field("object.tip.message", message)
                .time(timestamp)
            )
            self.event_repository.write_point(point)
        
        # Prepare data for WebSocket
        data = {
            "type": "tip",
            "username": username,
            "amount": amount,
            "message": message,
            "timestamp": timestamp.timestamp()
        }
        
        # Broadcast via WebSocket
        if self.socketio:
            self.socketio.emit("chaturbate_event", data, namespace="/chaturbate")
        
        self._stats["tips_processed"] += 1
        logger.info(f"Processed tip: {username} tipped {amount} tokens")
        
        return data
    
    async def _process_chat_event(self, event: Any, timestamp: datetime) -> Dict[str, Any]:
        """Process a chat message event."""
        username = event.object.user.username if event.object and event.object.user else "Anonymous"
        message = event.object.message if event.object else ""
        
        # Determine if system message
        method = "system" if username == "System" else "chatMessage"
        event_type = "system" if username == "System" else "chat"
        
        # Store in InfluxDB
        if self.event_repository:
            point = (
                Point("chaturbate_events")
                .tag("method", method)
                .tag("username", username)
                .field("object.user.username", username)
                .field("object.message", message)
                .time(timestamp)
            )
            self.event_repository.write_point(point)
        
        # Prepare data for WebSocket
        data = {
            "type": event_type,
            "username": username,
            "message": message,
            "timestamp": timestamp.timestamp()
        }
        
        # Broadcast via WebSocket
        if self.socketio:
            self.socketio.emit("chaturbate_event", data, namespace="/chaturbate")
        
        self._stats["messages_processed"] += 1
        logger.debug(f"Processed chat: {username}: {message[:50]}...")
        
        return data
    
    async def _process_private_message_event(self, event: Any, timestamp: datetime) -> Dict[str, Any]:
        """Process a private message event."""
        from_username = event.object.user.username if event.object and event.object.user else "Anonymous"
        message = event.object.message if event.object else ""
        
        # For demo purposes, using hardcoded recipient
        to_username = "google-oauth2|101763761877997490084"
        
        # Store in InfluxDB
        if self.event_repository:
            point = (
                Point("chaturbate_events")
                .tag("method", "privateMessage")
                .tag("from_user", from_username)
                .tag("to_user", to_username)
                .tag("is_read", "false")
                .field("object.user.username", from_username)
                .field("object.message", message)
                .field("from_user", from_username)
                .field("to_user", to_username)
                .time(timestamp)
            )
            self.event_repository.write_point(point)
        
        # Prepare data for WebSocket
        data = {
            "type": "private_message",
            "from_username": from_username,
            "to_username": to_username,
            "message": message,
            "timestamp": timestamp.timestamp()
        }
        
        # Broadcast via WebSocket
        if self.socketio:
            self.socketio.emit("chaturbate_event", data, namespace="/chaturbate")
        
        self._stats["private_messages_processed"] += 1
        logger.info(f"Processed private message: {from_username} -> {to_username}")
        
        return data
    
    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return self._stats.copy()
    
    def process_raw_event(self, data: Dict[str, Any]) -> Optional[BaseEvent]:
        """Process raw event data and convert to domain model.
        
        Args:
            data: Raw event data from Chaturbate
            
        Returns:
            Parsed event or None if parsing fails
        """
        try:
            method = data.get("method", "")
            event = self._parse_event(method, data)
            
            if event:
                # Process with specific handlers
                for handler in self.event_handlers.get(event.event_type, []):
                    try:
                        handler(event)
                    except Exception as e:
                        logger.error(f"Handler error for {event.event_type}: {e}")
                
                # Process with global handlers
                for handler in self.global_handlers:
                    try:
                        handler(event)
                    except Exception as e:
                        logger.error(f"Global handler error: {e}")
                        
            return event
            
        except Exception as e:
            logger.error(f"Failed to process event: {e}")
            return None
    
    def _parse_event(self, method: str, data: Dict[str, Any]) -> Optional[BaseEvent]:
        """Parse raw data into specific event type.
        
        Args:
            method: The event method/type
            data: Raw event data
            
        Returns:
            Parsed event or None
        """
        timestamp = datetime.utcnow()
        room = data.get("room", "")
        broadcaster = data.get("broadcaster", room)
        
        if method == "tip":
            return self._parse_tip_event(data, timestamp, room, broadcaster)
        elif method == "chatMessage":
            return self._parse_message_event(data, timestamp, room, broadcaster)
        elif method == "privateMessage":
            return self._parse_private_message_event(data, timestamp, room, broadcaster)
        elif method == "userJoin":
            return self._parse_user_join_event(data, timestamp, room, broadcaster)
        elif method == "userLeave":
            return self._parse_user_leave_event(data, timestamp, room, broadcaster)
        elif method == "mediaPurchase":
            return self._parse_media_purchase_event(data, timestamp, room, broadcaster)
        else:
            logger.warning(f"Unknown event method: {method}")
            return None
    
    def _parse_tip_event(self, data: Dict[str, Any], timestamp: datetime, 
                        room: str, broadcaster: str) -> Optional[TipEvent]:
        """Parse tip event."""
        try:
            user_data = data.get("user", {})
            tip_data = data.get("object", {}).get("tip", {})
            
            user = User.from_dict(user_data)
            
            return TipEvent(
                timestamp=timestamp,
                room=room,
                broadcaster=broadcaster,
                user=user,
                tokens=tip_data.get("tokens", 0),
                message=tip_data.get("message", ""),
                is_anonymous=tip_data.get("is_anonymous", False)
            )
        except Exception as e:
            logger.error(f"Failed to parse tip event: {e}")
            return None
    
    def _parse_message_event(self, data: Dict[str, Any], timestamp: datetime,
                           room: str, broadcaster: str) -> Optional[MessageEvent]:
        """Parse chat message event."""
        try:
            user_data = data.get("user", {})
            message_data = data.get("object", {}).get("message", {})
            
            user = User.from_dict(user_data)
            
            return MessageEvent(
                timestamp=timestamp,
                room=room,
                broadcaster=broadcaster,
                user=user,
                message=message_data.get("message", ""),
                color=message_data.get("color"),
                font=message_data.get("font")
            )
        except Exception as e:
            logger.error(f"Failed to parse message event: {e}")
            return None
    
    def _parse_private_message_event(self, data: Dict[str, Any], timestamp: datetime,
                                   room: str, broadcaster: str) -> Optional[PrivateMessageEvent]:
        """Parse private message event."""
        try:
            return PrivateMessageEvent(
                timestamp=timestamp,
                room=room,
                broadcaster=broadcaster,
                from_user=data.get("from_user", ""),
                to_user=data.get("to_user", ""),
                message=data.get("message", ""),
                tokens=data.get("tokens", 0)
            )
        except Exception as e:
            logger.error(f"Failed to parse private message event: {e}")
            return None
    
    def _parse_user_join_event(self, data: Dict[str, Any], timestamp: datetime,
                             room: str, broadcaster: str) -> Optional[UserJoinEvent]:
        """Parse user join event."""
        try:
            user_data = data.get("user", {})
            user = User.from_dict(user_data)
            
            return UserJoinEvent(
                timestamp=timestamp,
                room=room,
                broadcaster=broadcaster,
                user=user
            )
        except Exception as e:
            logger.error(f"Failed to parse user join event: {e}")
            return None
    
    def _parse_user_leave_event(self, data: Dict[str, Any], timestamp: datetime,
                              room: str, broadcaster: str) -> Optional[UserLeaveEvent]:
        """Parse user leave event."""
        try:
            user_data = data.get("user", {})
            user = User.from_dict(user_data)
            
            return UserLeaveEvent(
                timestamp=timestamp,
                room=room,
                broadcaster=broadcaster,
                user=user
            )
        except Exception as e:
            logger.error(f"Failed to parse user leave event: {e}")
            return None
    
    def _parse_media_purchase_event(self, data: Dict[str, Any], timestamp: datetime,
                                  room: str, broadcaster: str) -> Optional[MediaPurchaseEvent]:
        """Parse media purchase event."""
        try:
            user_data = data.get("user", {})
            media_data = data.get("object", {}).get("media", {})
            
            user = User.from_dict(user_data)
            
            return MediaPurchaseEvent(
                timestamp=timestamp,
                room=room,
                broadcaster=broadcaster,
                user=user,
                media_type=media_data.get("type", ""),
                media_name=media_data.get("name", ""),
                tokens=media_data.get("tokens", 0)
            )
        except Exception as e:
            logger.error(f"Failed to parse media purchase event: {e}")
            return None