import logging
from flask import request
from flask_socketio import emit
from typing import Dict, Any

from core.dependencies import get_websocket_service, get_event_service, get_event_repository
from models.events import BaseEvent

logger = logging.getLogger(__name__)


class ChaturbateWebSocketHandler:
    """Handler for Chaturbate WebSocket connections."""
    
    def __init__(self):
        self.websocket_service = get_websocket_service()
        self.event_service = get_event_service()
        self.event_repository = get_event_repository()
        
        # Register event handlers
        self._register_event_handlers()
        
    def _register_event_handlers(self):
        """Register handlers for different event types."""
        # WebSocket broadcast handler
        self.event_service.register_global_handler(self._handle_websocket_broadcast)
        
        # InfluxDB storage handler (if repository available)
        if self.event_repository:
            self.event_service.register_global_handler(self._handle_influx_storage)
        
    def handle_connect(self) -> None:
        """Handle client connection."""
        client_id = request.sid
        self.websocket_service.register_client(client_id)
        
        emit("connected", {
            "status": "connected",
            "client_id": client_id,
            "message": "Connected to Chaturbate event stream"
        })
        
        logger.info(f"Client connected: {client_id}")
        
    def handle_disconnect(self) -> None:
        """Handle client disconnection."""
        client_id = request.sid
        self.websocket_service.unregister_client(client_id)
        logger.info(f"Client disconnected: {client_id}")
        
    def handle_subscribe(self, data: Dict[str, Any]) -> None:
        """Handle room subscription request.
        
        Args:
            data: Subscription data containing room information
        """
        client_id = request.sid
        room = data.get("room")
        
        if not room:
            emit("error", {"error": "Room name required"})
            return
            
        self.websocket_service.subscribe_to_room(client_id, room)
        emit("subscribed", {
            "room": room,
            "status": "subscribed"
        })
        
        logger.info(f"Client {client_id} subscribed to room: {room}")
        
    def handle_unsubscribe(self, data: Dict[str, Any]) -> None:
        """Handle room unsubscription request.
        
        Args:
            data: Unsubscription data containing room information
        """
        client_id = request.sid
        room = data.get("room")
        
        if not room:
            emit("error", {"error": "Room name required"})
            return
            
        self.websocket_service.unsubscribe_from_room(client_id, room)
        emit("unsubscribed", {
            "room": room,
            "status": "unsubscribed"
        })
        
        logger.info(f"Client {client_id} unsubscribed from room: {room}")
        
    def handle_event(self, data: Dict[str, Any]) -> None:
        """Handle incoming Chaturbate event.
        
        Args:
            data: Raw event data from Chaturbate
        """
        # Process the event through the event service
        event = self.event_service.process_raw_event(data)
        
        if event:
            emit("event_processed", {
                "status": "processed",
                "event_type": event.event_type.value
            })
        else:
            emit("event_error", {
                "status": "error",
                "message": "Failed to process event"
            })
            
    def _handle_websocket_broadcast(self, event: BaseEvent) -> None:
        """Handler to broadcast events via WebSocket.
        
        Args:
            event: The event to broadcast
        """
        try:
            self.websocket_service.broadcast_event(event)
        except Exception as e:
            logger.error(f"Failed to broadcast event: {e}")
            
    def _handle_influx_storage(self, event: BaseEvent) -> None:
        """Handler to store events in InfluxDB.
        
        Args:
            event: The event to store
        """
        try:
            if self.event_repository:
                success = self.event_repository.save(event)
                if success:
                    logger.debug(f"Stored {event.event_type.value} event to InfluxDB")
                else:
                    logger.warning(f"Failed to store {event.event_type.value} event")
        except Exception as e:
            logger.error(f"Failed to store event in InfluxDB: {e}")


def register_websocket_handlers(socketio):
    """Register WebSocket handlers with SocketIO.
    
    Args:
        socketio: The SocketIO instance
    """
    handler = ChaturbateWebSocketHandler()
    
    @socketio.on("connect", namespace="/chaturbate")
    def on_connect():
        handler.handle_connect()
        
    @socketio.on("disconnect", namespace="/chaturbate")
    def on_disconnect():
        handler.handle_disconnect()
        
    @socketio.on("subscribe", namespace="/chaturbate")
    def on_subscribe(data):
        handler.handle_subscribe(data)
        
    @socketio.on("unsubscribe", namespace="/chaturbate")
    def on_unsubscribe(data):
        handler.handle_unsubscribe(data)
        
    @socketio.on("event", namespace="/chaturbate")
    def on_event(data):
        handler.handle_event(data)
        
    logger.info("Registered Chaturbate WebSocket handlers")