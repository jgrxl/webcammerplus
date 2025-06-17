import logging
from typing import Dict, Any, Set, Optional
from flask_socketio import SocketIO
from models.events import BaseEvent

logger = logging.getLogger(__name__)


class WebSocketService:
    """Service for managing WebSocket connections and broadcasting events."""
    
    def __init__(self, socketio: Optional[SocketIO] = None):
        self.socketio = socketio
        self.connected_clients: Set[str] = set()
        self.client_subscriptions: Dict[str, Set[str]] = {}  # client_id -> set of rooms
        
    def set_socketio(self, socketio: SocketIO) -> None:
        """Set the SocketIO instance (for late initialization)."""
        self.socketio = socketio
        
    def register_client(self, client_id: str) -> None:
        """Register a new WebSocket client.
        
        Args:
            client_id: The client's session ID
        """
        self.connected_clients.add(client_id)
        self.client_subscriptions[client_id] = set()
        logger.info(f"Client connected: {client_id}")
        
    def unregister_client(self, client_id: str) -> None:
        """Unregister a WebSocket client.
        
        Args:
            client_id: The client's session ID
        """
        self.connected_clients.discard(client_id)
        self.client_subscriptions.pop(client_id, None)
        logger.info(f"Client disconnected: {client_id}")
        
    def subscribe_to_room(self, client_id: str, room: str) -> None:
        """Subscribe a client to a specific room's events.
        
        Args:
            client_id: The client's session ID
            room: The room to subscribe to
        """
        if client_id in self.client_subscriptions:
            self.client_subscriptions[client_id].add(room)
            logger.info(f"Client {client_id} subscribed to room: {room}")
            
    def unsubscribe_from_room(self, client_id: str, room: str) -> None:
        """Unsubscribe a client from a room's events.
        
        Args:
            client_id: The client's session ID
            room: The room to unsubscribe from
        """
        if client_id in self.client_subscriptions:
            self.client_subscriptions[client_id].discard(room)
            logger.info(f"Client {client_id} unsubscribed from room: {room}")
            
    def broadcast_event(self, event: BaseEvent) -> None:
        """Broadcast an event to all subscribed clients.
        
        Args:
            event: The event to broadcast
        """
        if not self.socketio:
            logger.warning("SocketIO not initialized, cannot broadcast event")
            return
            
        event_data = {
            "type": event.event_type.value,
            "data": event.to_dict(),
            "timestamp": event.timestamp.isoformat()
        }
        
        # Broadcast to all clients subscribed to this room
        room = event.room
        broadcast_count = 0
        
        for client_id, rooms in self.client_subscriptions.items():
            if room in rooms or "*" in rooms:  # "*" means subscribe to all rooms
                self.socketio.emit(
                    "chaturbate_event",
                    event_data,
                    room=client_id
                )
                broadcast_count += 1
                
        logger.debug(f"Broadcasted {event.event_type.value} event to {broadcast_count} clients")
        
    def broadcast_to_all(self, event_name: str, data: Dict[str, Any]) -> None:
        """Broadcast a custom event to all connected clients.
        
        Args:
            event_name: The event name
            data: The event data
        """
        if not self.socketio:
            logger.warning("SocketIO not initialized, cannot broadcast")
            return
            
        self.socketio.emit(event_name, data, broadcast=True)
        logger.debug(f"Broadcasted {event_name} to all clients")
        
    def send_to_client(self, client_id: str, event_name: str, data: Dict[str, Any]) -> None:
        """Send an event to a specific client.
        
        Args:
            client_id: The client's session ID
            event_name: The event name
            data: The event data
        """
        if not self.socketio:
            logger.warning("SocketIO not initialized, cannot send to client")
            return
            
        if client_id in self.connected_clients:
            self.socketio.emit(event_name, data, room=client_id)
            logger.debug(f"Sent {event_name} to client {client_id}")
        else:
            logger.warning(f"Client {client_id} not connected")
            
    def get_connected_clients_count(self) -> int:
        """Get the number of connected clients."""
        return len(self.connected_clients)
        
    def get_room_subscribers_count(self, room: str) -> int:
        """Get the number of clients subscribed to a room."""
        count = 0
        for rooms in self.client_subscriptions.values():
            if room in rooms:
                count += 1
        return count