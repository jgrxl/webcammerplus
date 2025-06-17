import asyncio
import logging
import random
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Set

from flask import request
from flask_restx import Namespace, Resource
from flask_socketio import SocketIO, emit

from core.dependencies import get_dependency, get_event_repository
from services.chaturbate_event_service import EventProcessingService
from services.demo_event_service import DemoEventService

logger = logging.getLogger(__name__)

api = Namespace("chaturbate", description="Chaturbate WebSocket operations")

# Global storage for WebSocket connections and demo client
connected_clients: Set[str] = set()
demo_client_running: bool = False
socketio: Optional[SocketIO] = None
demo_service: Optional[DemoEventService] = None
demo_task: Optional[asyncio.Task] = None


# Create mock objects that match the chaturbate_poller structure
@dataclass
class MockUser:
    username: str


@dataclass
class MockTip:
    tokens: int
    message: str = ""


@dataclass
class MockTipObject:
    user: MockUser
    tip: MockTip
    message: str = ""


@dataclass
class MockChatObject:
    user: MockUser
    message: str


@dataclass
class MockEvent:
    object: any
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


# Import the real event handler and models
from client.chaturbate_client_event_handler import ChaturbateClientEventHandler

logger.info("Using real ChaturbateClientEventHandler with chaturbate_poller models")


class WebSocketEventHandler(ChaturbateClientEventHandler):
    """Event handler that uses EventProcessingService for storage and broadcasting."""

    def __init__(self, socket_io: SocketIO):
        super().__init__(enable_logging=True)
        self.socketio = socket_io
        self.event_service = get_dependency(EventProcessingService)
        self.event_service.set_socketio(socket_io)
        
        # Set event repository if available
        event_repo = get_event_repository()
        if event_repo:
            self.event_service.set_event_repository(event_repo)
            logger.info("Event repository configured for WebSocketEventHandler")
        else:
            logger.warning("No event repository available - events won't be persisted")

    async def handle_tip(self, event) -> None:
        """Handle tip events using EventProcessingService."""
        try:
            # Process with parent handler first
            await super().handle_tip(event)
            
            # Use event service for storage and broadcasting
            await self.event_service.process_and_store_event(event, "tip")
            
        except Exception as e:
            logger.error(f"Error handling tip event: {e}")

    async def handle_chat(self, event) -> None:
        """Handle chat events using EventProcessingService."""
        try:
            # Process with parent handler first
            await super().handle_chat(event)
            
            # Use event service for storage and broadcasting
            await self.event_service.process_and_store_event(event, "chat")
            
        except Exception as e:
            logger.error(f"Error handling chat event: {e}")

    async def handle_message(self, event) -> None:
        """Handle generic message events and forward to WebSocket."""
        try:
            # Process with parent handler first
            await super().handle_message(event)

            if event and event.object:
                data = {
                    "type": "message",
                    "message": str(event.object),
                    "timestamp": event.timestamp.timestamp(),
                }

                self.socketio.emit("chaturbate_event", data, namespace="/chaturbate")
                logger.debug(f"Processed and forwarded generic message event")

        except Exception as e:
            logger.error(f"Error handling message event: {e}")

    async def handle_private_message(self, event) -> None:
        """Handle private message events using EventProcessingService."""
        try:
            # Process with parent handler first
            await super().handle_private_message(event)
            
            # Use event service for storage and broadcasting
            await self.event_service.process_and_store_event(event, "private_message")

        except Exception as e:
            logger.error(f"Error handling private message event: {e}")


# DemoEventGenerator class removed - using DemoEventService instead
event_handler: Optional[WebSocketEventHandler] = None


def setup_socketio(app, socket_io: SocketIO):
    """Setup SocketIO event handlers for Chaturbate connections."""
    global socketio, demo_service, event_handler
    socketio = socket_io
    event_handler = WebSocketEventHandler(socketio)
    
    # Get demo service and configure it
    demo_service = get_dependency(DemoEventService)
    demo_service.set_event_handler(event_handler)

    @socket_io.on("connect", namespace="/chaturbate")
    def handle_connect():
        """Handle WebSocket connection."""
        client_id = request.sid
        connected_clients.add(client_id)
        logger.info(f"Client {client_id} connected to Chaturbate WebSocket")

        # Send connection confirmation
        emit("connection_status", {"status": "connected"})

        # Start demo client if not already running
        start_demo_client()

    @socket_io.on("disconnect", namespace="/chaturbate")
    def handle_disconnect():
        """Handle WebSocket disconnection."""
        client_id = request.sid
        connected_clients.discard(client_id)
        logger.info(f"Client {client_id} disconnected from Chaturbate WebSocket")

        # Stop demo client if no clients connected
        if not connected_clients:
            stop_demo_client()

    @socket_io.on("start_chaturbate", namespace="/chaturbate")
    def handle_start_chaturbate():
        """Handle request to start Chaturbate client."""
        start_demo_client()

    @socket_io.on("stop_chaturbate", namespace="/chaturbate")
    def handle_stop_chaturbate():
        """Handle request to stop Chaturbate client."""
        stop_demo_client()


def start_demo_client():
    """Start demo Chaturbate client."""
    global demo_client_running, demo_task

    if demo_client_running:
        logger.info("Demo client is already running")
        return

    try:
        demo_client_running = True
        logger.info("Starting demo Chaturbate client with event handler processing")

        # Send status update
        if socketio:
            socketio.emit(
                "chaturbate_status", {"status": "starting"}, namespace="/chaturbate"
            )

        # Start demo event generator in a separate thread with its own event loop
        if demo_service:
            def run_demo():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Send initial system message
                loop.run_until_complete(demo_service.generate_chat_event())
                
                # Run the demo loop
                loop.run_until_complete(demo_service.run_demo_loop())
            
            import threading
            demo_task = threading.Thread(target=run_demo, daemon=True)
            demo_task.start()

        if socketio:
            socketio.emit(
                "chaturbate_status", {"status": "running"}, namespace="/chaturbate"
            )

        logger.info(
            "Demo client started successfully - events will go through ChaturbateClientEventHandler"
        )

    except Exception as e:
        error_msg = f"Failed to start demo client: {str(e)}"
        logger.error(error_msg)
        demo_client_running = False
        if socketio:
            socketio.emit(
                "chaturbate_error", {"error": error_msg}, namespace="/chaturbate"
            )


def stop_demo_client():
    """Stop demo Chaturbate client."""
    global demo_client_running, demo_task

    if not demo_client_running:
        logger.info("Demo client is not running")
        return

    try:
        logger.info("Stopping demo Chaturbate client")
        demo_client_running = False

        if socketio:
            socketio.emit(
                "chaturbate_status", {"status": "stopping"}, namespace="/chaturbate"
            )

        # Stop demo event generator
        if demo_service:
            demo_service.stop()

        # Cancel the task if it exists
        if demo_task and not demo_task.done():
            demo_task.cancel()

        if socketio:
            socketio.emit(
                "chaturbate_status", {"status": "stopped"}, namespace="/chaturbate"
            )

        logger.info("Demo client stopped successfully")

    except Exception as e:
        error_msg = f"Error stopping demo client: {str(e)}"
        logger.error(error_msg)
        if socketio:
            socketio.emit(
                "chaturbate_error", {"error": error_msg}, namespace="/chaturbate"
            )


@api.route("/status")
class ChaturbateStatus(Resource):
    def get(self):
        """Get current Chaturbate client status."""
        global demo_client_running

        status = {
            "running": demo_client_running,
            "connected_clients": len(connected_clients),
            "has_credentials": True,  # Always true for demo
            "demo_mode": True,
            "using_real_handler": True,
            "handler_type": "ChaturbateClientEventHandler",
        }

        # Add event stats if handler is available
        if event_handler and hasattr(event_handler, "get_stats"):
            status["event_stats"] = event_handler.get_stats()

        return status


@api.route("/start")
class ChaturbateStart(Resource):
    def post(self):
        """Start Chaturbate client manually."""
        start_demo_client()
        return {"message": "Demo Chaturbate client start requested"}


@api.route("/stop")
class ChaturbateStop(Resource):
    def post(self):
        """Stop Chaturbate client manually."""
        stop_demo_client()
        return {"message": "Demo Chaturbate client stop requested"}
