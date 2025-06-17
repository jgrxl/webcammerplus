"""Demo event generation service for testing Chaturbate integration.

This service generates realistic mock events for development and testing purposes.
"""

import asyncio
import logging
import random
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DemoEventService:
    """Service for generating demo Chaturbate events."""
    
    # Demo data pools
    DEMO_USERS = [
        "CoolUser123", "HotStuff99", "MidnightDancer", "SunnySmiles",
        "WildHeart22", "MysticMoon", "FireFly88", "DiamondEyes",
        "SweetDreams", "NightOwl77", "GoldenStar", "BlueSky21",
        "RedRose44", "SilverFox", "PurpleRain", "GreenThumb",
        "System", "Moderator", "VIPUser", "RegularFan"
    ]
    
    DEMO_MESSAGES = [
        "Hey everyone! 👋", "This stream is amazing!", "Love the show!",
        "Hello from Brazil 🇧🇷", "First time here, loving it!",
        "You're the best!", "Great music choice!", "Can't stop watching!",
        "Greetings from Germany 🇩🇪", "This is so much fun!",
        "You make my day better", "Incredible performance!",
        "Hello beautiful people!", "Best stream ever!", "Keep it up!",
        "Sending love ❤️", "You're awesome!", "This is lit! 🔥",
        "Amazing energy tonight!", "Can't believe how good this is!"
    ]
    
    DEMO_TIP_MESSAGES = [
        "Keep up the great work!", "For your amazing show!",
        "You deserve this!", "Love what you do!", "Amazing performance!",
        "Thanks for the entertainment!", "You're incredible!",
        "Best streamer ever!", "Take my tokens!", "Worth every token!",
        "For being awesome!", "Keep shining!", "You rock!",
        "Appreciate you!", "This is for you!", "Well deserved!",
        "Great job!", "Love your content!", "You're the best!",
        "Supporting you always!"
    ]
    
    TIP_AMOUNTS = [1, 5, 10, 15, 20, 25, 50, 100, 200, 500, 1000]
    TIP_WEIGHTS = [30, 25, 20, 10, 5, 3, 3, 2, 1, 0.8, 0.2]
    
    def __init__(self, event_handler: Optional[Any] = None):
        """Initialize the demo event service.
        
        Args:
            event_handler: Handler to process generated events
        """
        self.event_handler = event_handler
        self.running = False
        self.event_count = 0
        self.last_event_time = datetime.now()
        
    def set_event_handler(self, handler: Any) -> None:
        """Set the event handler for processing generated events.
        
        Args:
            handler: The event handler instance
        """
        self.event_handler = handler
        logger.info("Event handler set for DemoEventService")
    
    def _create_mock_user(self, username: str) -> Any:
        """Create a mock user object."""
        from dataclasses import dataclass
        
        @dataclass
        class MockUser:
            username: str
        
        return MockUser(username=username)
    
    def _create_mock_tip(self, amount: int, message: str = "") -> Any:
        """Create a mock tip object."""
        from dataclasses import dataclass
        
        @dataclass
        class MockTip:
            tokens: int
            message: str = ""
        
        return MockTip(tokens=amount, message=message)
    
    def _create_mock_event(self, event_object: Any) -> Any:
        """Create a mock event wrapper."""
        from dataclasses import dataclass
        
        @dataclass
        class MockEvent:
            object: Any
            timestamp: datetime = None
            
            def __post_init__(self):
                if self.timestamp is None:
                    self.timestamp = datetime.now()
        
        return MockEvent(object=event_object)
    
    async def generate_tip_event(self) -> Dict[str, Any]:
        """Generate a random tip event."""
        username = random.choice([u for u in self.DEMO_USERS if u not in ["System", "Moderator"]])
        amount = random.choices(self.TIP_AMOUNTS, weights=self.TIP_WEIGHTS)[0]
        message = random.choice(self.DEMO_TIP_MESSAGES) if random.random() > 0.3 else ""
        
        # Create mock objects
        user = self._create_mock_user(username)
        tip = self._create_mock_tip(amount, message)
        
        # Create tip object
        from dataclasses import dataclass
        
        @dataclass
        class MockTipObject:
            user: Any
            tip: Any
            message: str = ""
        
        tip_object = MockTipObject(user=user, tip=tip, message=message)
        event = self._create_mock_event(tip_object)
        
        # Process with handler if available
        if self.event_handler:
            await self.event_handler.handle_tip(event)
        
        logger.info(f"Generated tip event: {username} tipped {amount} tokens")
        return {
            "type": "tip",
            "username": username,
            "amount": amount,
            "message": message,
            "timestamp": event.timestamp.timestamp()
        }
    
    async def generate_chat_event(self) -> Dict[str, Any]:
        """Generate a random chat message event."""
        username = random.choice(self.DEMO_USERS)
        message = random.choice(self.DEMO_MESSAGES)
        
        # Create mock objects
        user = self._create_mock_user(username)
        
        from dataclasses import dataclass
        
        @dataclass
        class MockChatObject:
            user: Any
            message: str
        
        chat_object = MockChatObject(user=user, message=message)
        event = self._create_mock_event(chat_object)
        
        # Process with handler if available
        if self.event_handler:
            await self.event_handler.handle_chat(event)
        
        logger.debug(f"Generated chat event: {username}: {message}")
        return {
            "type": "chat" if username != "System" else "system",
            "username": username,
            "message": message,
            "timestamp": event.timestamp.timestamp()
        }
    
    async def generate_private_message_event(self) -> Dict[str, Any]:
        """Generate a random private message event."""
        from_username = random.choice([u for u in self.DEMO_USERS if u not in ["System", "Moderator"]])
        message = f"Private: {random.choice(self.DEMO_MESSAGES)}"
        
        # Create mock objects
        user = self._create_mock_user(from_username)
        
        from dataclasses import dataclass
        
        @dataclass
        class MockPrivateMessageObject:
            user: Any
            message: str
        
        pm_object = MockPrivateMessageObject(user=user, message=message)
        event = self._create_mock_event(pm_object)
        
        # Process with handler if available
        if self.event_handler:
            await self.event_handler.handle_private_message(event)
        
        logger.info(f"Generated private message event from {from_username}")
        return {
            "type": "private_message",
            "from_username": from_username,
            "message": message,
            "timestamp": event.timestamp.timestamp()
        }
    
    async def run_demo_loop(self) -> None:
        """Run the demo event generation loop."""
        self.running = True
        logger.info("Starting demo event generation loop")
        
        try:
            while self.running:
                # Generate events with realistic frequency
                event_type = random.choices(
                    ["chat", "tip", "private_message"],
                    weights=[70, 25, 5]
                )[0]
                
                if event_type == "chat":
                    await self.generate_chat_event()
                    await asyncio.sleep(random.uniform(2, 8))
                elif event_type == "tip":
                    await self.generate_tip_event()
                    await asyncio.sleep(random.uniform(10, 30))
                else:  # private_message
                    await self.generate_private_message_event()
                    await asyncio.sleep(random.uniform(30, 60))
                
                self.event_count += 1
                self.last_event_time = datetime.now()
                
        except asyncio.CancelledError:
            logger.info("Demo event generation cancelled")
        except Exception as e:
            logger.error(f"Error in demo event loop: {e}")
        finally:
            self.running = False
            logger.info(f"Demo event generation stopped. Total events: {self.event_count}")
    
    def stop(self) -> None:
        """Stop the demo event generation."""
        self.running = False
        logger.info("Stopping demo event generation")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get demo generation statistics."""
        return {
            "running": self.running,
            "event_count": self.event_count,
            "last_event_time": self.last_event_time.isoformat() if self.last_event_time else None
        }