import asyncio
import json
import logging
import threading
import time
import random
from typing import Dict, Set, Optional
from flask import request
from flask_restx import Namespace, Resource
from flask_socketio import SocketIO, emit, disconnect
import os
from dataclasses import dataclass
from datetime import datetime
from client.influx_client import InfluxDBClient
from influxdb_client import Point


logger = logging.getLogger(__name__)

api = Namespace('chaturbate', description='Chaturbate WebSocket operations')

# Global storage for WebSocket connections and demo client
connected_clients: Set[str] = set()
demo_client_running: bool = False
socketio: Optional[SocketIO] = None


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
    """Event handler that forwards processed events to WebSocket clients and stores them in InfluxDB."""
    
    def __init__(self, socket_io: SocketIO):
        super().__init__(enable_logging=True)
        self.socketio = socket_io
        self.influx_client = None
        self._init_influx_client()
    
    def _init_influx_client(self):
        """Initialize InfluxDB client if environment variables are set."""
        try:
            self.influx_client = InfluxDBClient()
            logger.info("InfluxDB client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize InfluxDB client: {e}")
            self.influx_client = None
    
    def _write_to_influx(self, point: Point):
        """Write a point to InfluxDB if client is available."""
        if self.influx_client:
            try:
                write_api = self.influx_client.write_api
                write_api.write(bucket=self.influx_client.bucket, org=self.influx_client.org, record=point)
                logger.info(f"Successfully wrote event to InfluxDB: {point._name} for user: {point._tags.get('username', 'unknown')}")
            except Exception as e:
                logger.error(f"Failed to write to InfluxDB: {e}")
        else:
            logger.warning("InfluxDB client not available - skipping write")
    
    async def handle_tip(self, event) -> None:
        """Handle tip events, write to InfluxDB, and forward to WebSocket."""
        try:
            # Process with parent handler first
            await super().handle_tip(event)
            
            if event and event.object and event.object.user and event.object.tip:
                username = event.object.user.username or "Anonymous"
                amount = event.object.tip.tokens or 0
                message = getattr(event.object.tip, 'message', '') or event.object.message or ''
                
                # Write to InfluxDB
                point = Point("chaturbate_events") \
                    .tag("method", "tip") \
                    .tag("username", username) \
                    .field("object.tip.tokens", amount) \
                    .field("object.user.username", username) \
                    .field("object.tip.message", message) \
                    .time(event.timestamp)
                
                self._write_to_influx(point)
                
                data = {
                    'type': 'tip',
                    'username': username,
                    'amount': amount,
                    'message': message,
                    'timestamp': event.timestamp.timestamp()
                }
                
                self.socketio.emit('chaturbate_event', data, namespace='/chaturbate')
                logger.info(f"Processed tip event to InfluxDB and WebSocket: {username} tipped {amount} tokens")
                
        except Exception as e:
            logger.error(f"Error handling tip event: {e}")
    
    async def handle_chat(self, event) -> None:
        """Handle chat events, write to InfluxDB, and forward to WebSocket."""
        try:
            # Process with parent handler first
            await super().handle_chat(event)
            
            if event and event.object and event.object.user:
                username = event.object.user.username or "Anonymous"
                message = event.object.message or ""
                
                # Write to InfluxDB
                point = Point("chaturbate_events") \
                    .tag("method", "chatMessage") \
                    .tag("username", username) \
                    .field("object.user.username", username) \
                    .field("object.message", message) \
                    .time(event.timestamp)
                
                self._write_to_influx(point)
                
                data = {
                    'type': 'chat',
                    'username': username,
                    'message': message,
                    'timestamp': event.timestamp.timestamp()
                }
                
                self.socketio.emit('chaturbate_event', data, namespace='/chaturbate')
                logger.debug(f"Processed chat event to InfluxDB and WebSocket: {username}: {message[:50]}...")
                
        except Exception as e:
            logger.error(f"Error handling chat event: {e}")
    
    async def handle_message(self, event) -> None:
        """Handle generic message events and forward to WebSocket."""
        try:
            # Process with parent handler first
            await super().handle_message(event)
            
            if event and event.object:
                data = {
                    'type': 'message',
                    'message': str(event.object),
                    'timestamp': event.timestamp.timestamp()
                }
                
                self.socketio.emit('chaturbate_event', data, namespace='/chaturbate')
                logger.debug(f"Processed and forwarded generic message event")
                
        except Exception as e:
            logger.error(f"Error handling message event: {e}")


class DemoEventGenerator:
    """Demo event generator that creates proper event objects and processes them through the event handler."""
    
    def __init__(self, event_handler: WebSocketEventHandler):
        self.event_handler = event_handler
        self.running = False
        
    def start(self):
        """Start generating demo events."""
        if self.running:
            return
            
        self.running = True
        logger.info("Starting demo event generator with real event handler processing")
        
        def generate_events():
            while self.running and connected_clients:
                try:
                    # Generate random events and process them through the event handler
                    # Increase tip frequency to 70% tips, 30% chat
                    event_type = random.choices(['tip', 'chat'], weights=[70, 30], k=1)[0]
                    
                    if event_type == 'tip':
                        # Create a proper tip event object matching real Chaturbate structure
                        # Use consistent usernames with different tip patterns
                        tipper_profiles = [
                            ('WhaleKing', [100, 200, 500, 1000]),  # Big spender
                            ('DiamondHands', [50, 100, 200, 500]),  # Generous regular
                            ('LoyalFan', [25, 50, 100, 100]),  # Consistent tipper
                            ('NewSupporter', [10, 25, 50]),  # New supporter
                            ('RandomTipper', [5, 10, 25, 50]),  # Occasional tipper
                            ('BigSpender2024', [200, 500, 1000]),  # VIP
                            ('GenerousViewer', [100, 150, 200]),  # Premium supporter
                        ]
                        
                        # Pick a tipper profile
                        username, amounts = random.choice(tipper_profiles)
                        user = MockUser(username=username)
                        amount = random.choice(amounts)
                        tip_message = random.choice(['Thanks!', 'Great show!', 'Keep it up!', 'You\'re amazing!', 'Love the stream!', ''])
                        
                        tip = MockTip(tokens=amount, message=tip_message)
                        tip_object = MockTipObject(user=user, tip=tip, message=tip_message)
                        event = MockEvent(object=tip_object)
                        
                        # Process through the real event handler
                        self._run_async_handler(self.event_handler.handle_tip(event))
                        
                    elif event_type == 'chat':
                        # Create a proper chat event object
                        # Mix of tippers and regular chatters
                        chat_users = [
                            'WhaleKing', 'DiamondHands', 'LoyalFan', 'NewSupporter',
                            'ChatUser1', 'Viewer2', 'RegularFan', 'QuietViewer',
                            'BigSpender2024', 'GenerousViewer'
                        ]
                        user = MockUser(username=random.choice(chat_users))
                        chat_message = random.choice([
                            'Hello!', 'How are you?', 'Great stream!', 
                            'What time is it?', 'You look amazing!', '😍',
                            'Thanks for the show!', 'Keep up the good work!',
                            'When is the next stream?', 'Love your content!'
                        ])
                        
                        chat_object = MockChatObject(user=user, message=chat_message)
                        event = MockEvent(object=chat_object, timestamp=datetime.now())
                        
                        # Process through the real event handler
                        self._run_async_handler(self.event_handler.handle_chat(event))
                    
                    logger.debug(f"Generated and processed demo event: {event_type}")
                    
                    # Wait 1-3 seconds between events for more frequent tips
                    time.sleep(random.uniform(1, 3))
                    
                except Exception as e:
                    logger.error(f"Error generating demo event: {e}")
                    time.sleep(5)
            
            logger.info("Demo event generator stopped")
        
        # Start in background thread
        thread = threading.Thread(target=generate_events, daemon=True)
        thread.start()
    
    def stop(self):
        """Stop generating demo events."""
        self.running = False
        logger.info("Stopping demo event generator")
    
    def _run_async_handler(self, coro):
        """Run async handler in a new thread with event loop."""
        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(coro)
            finally:
                loop.close()
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()


demo_generator: Optional[DemoEventGenerator] = None
event_handler: Optional[WebSocketEventHandler] = None


def setup_socketio(app, socket_io: SocketIO):
    """Setup SocketIO event handlers for Chaturbate connections."""
    global socketio, demo_generator, event_handler
    socketio = socket_io
    event_handler = WebSocketEventHandler(socketio)
    demo_generator = DemoEventGenerator(event_handler)
    
    @socket_io.on('connect', namespace='/chaturbate')
    def handle_connect():
        """Handle WebSocket connection."""
        client_id = request.sid
        connected_clients.add(client_id)
        logger.info(f"Client {client_id} connected to Chaturbate WebSocket")
        
        # Send connection confirmation
        emit('connection_status', {'status': 'connected'})
        
        # Start demo client if not already running
        start_demo_client()
    
    @socket_io.on('disconnect', namespace='/chaturbate')
    def handle_disconnect():
        """Handle WebSocket disconnection."""
        client_id = request.sid
        connected_clients.discard(client_id)
        logger.info(f"Client {client_id} disconnected from Chaturbate WebSocket")
        
        # Stop demo client if no clients connected
        if not connected_clients:
            stop_demo_client()
    
    @socket_io.on('start_chaturbate', namespace='/chaturbate')
    def handle_start_chaturbate():
        """Handle request to start Chaturbate client."""
        start_demo_client()
    
    @socket_io.on('stop_chaturbate', namespace='/chaturbate')
    def handle_stop_chaturbate():
        """Handle request to stop Chaturbate client."""
        stop_demo_client()


def start_demo_client():
    """Start demo Chaturbate client."""
    global demo_client_running
    
    if demo_client_running:
        logger.info("Demo client is already running")
        return
    
    try:
        demo_client_running = True
        logger.info("Starting demo Chaturbate client with event handler processing")
        
        # Send status update
        if socketio:
            socketio.emit('chaturbate_status', {'status': 'starting'}, namespace='/chaturbate')
        
        # Send system message through event handler
        if event_handler:
            system_event = MockEvent(
                object=MockChatObject(
                    user=MockUser(username="System"),
                    message="Demo Chaturbate client started - events will be processed through handler"
                )
            )
            demo_generator._run_async_handler(event_handler.handle_chat(system_event))
        
        # Start demo event generator
        if demo_generator:
            demo_generator.start()
            
        if socketio:
            socketio.emit('chaturbate_status', {'status': 'running'}, namespace='/chaturbate')
        
        logger.info("Demo client started successfully - events will go through ChaturbateClientEventHandler")
        
    except Exception as e:
        error_msg = f"Failed to start demo client: {str(e)}"
        logger.error(error_msg)
        demo_client_running = False
        if socketio:
            socketio.emit('chaturbate_error', {'error': error_msg}, namespace='/chaturbate')


def stop_demo_client():
    """Stop demo Chaturbate client."""
    global demo_client_running
    
    if not demo_client_running:
        logger.info("Demo client is not running")
        return
    
    try:
        logger.info("Stopping demo Chaturbate client")
        demo_client_running = False
        
        if socketio:
            socketio.emit('chaturbate_status', {'status': 'stopping'}, namespace='/chaturbate')
        
        # Stop demo event generator
        if demo_generator:
            demo_generator.stop()
        
        # Send system message through event handler
        if event_handler and demo_generator:
            system_event = MockEvent(
                object=MockChatObject(
                    user=MockUser(username="System"),
                    message="Demo Chaturbate client stopped"
                )
            )
            demo_generator._run_async_handler(event_handler.handle_chat(system_event))
        
        if socketio:
            socketio.emit('chaturbate_status', {'status': 'stopped'}, namespace='/chaturbate')
        
        logger.info("Demo client stopped successfully")
        
    except Exception as e:
        error_msg = f"Error stopping demo client: {str(e)}"
        logger.error(error_msg)
        if socketio:
            socketio.emit('chaturbate_error', {'error': error_msg}, namespace='/chaturbate')


@api.route('/status')
class ChaturbateStatus(Resource):
    def get(self):
        """Get current Chaturbate client status."""
        global demo_client_running
        
        status = {
            'running': demo_client_running,
            'connected_clients': len(connected_clients),
            'has_credentials': True,  # Always true for demo
            'demo_mode': True,
            'using_real_handler': True,
            'handler_type': 'ChaturbateClientEventHandler'
        }
        
        # Add event stats if handler is available
        if event_handler and hasattr(event_handler, 'get_stats'):
            status['event_stats'] = event_handler.get_stats()
        
        return status


@api.route('/start')
class ChaturbateStart(Resource):
    def post(self):
        """Start Chaturbate client manually."""
        start_demo_client()
        return {'message': 'Demo Chaturbate client start requested'}


@api.route('/stop')
class ChaturbateStop(Resource):
    def post(self):
        """Stop Chaturbate client manually."""
        stop_demo_client()
        return {'message': 'Demo Chaturbate client stop requested'}