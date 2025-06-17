import random
import logging
from datetime import datetime, timedelta
from typing import List, Any, Optional
from models.events import (
    User, Gender, TipEvent, MessageEvent, UserJoinEvent, 
    UserLeaveEvent, MediaPurchaseEvent, PrivateMessageEvent
)

logger = logging.getLogger(__name__)


class DemoDataService:
    """Service for generating demo/test data."""
    
    def __init__(self):
        self.demo_users = self._generate_demo_users()
        self.demo_messages = [
            "Amazing show! 😍",
            "You're the best!",
            "Love your content",
            "Keep it up!",
            "So hot 🔥",
            "Can't get enough",
            "You're incredible",
            "Best room on CB",
            "Following you now!",
            "Take my tokens!",
            "Wow just wow",
            "Perfect as always",
            "You made my day",
            "Can't wait for more",
            "Absolutely stunning"
        ]
        
    def _generate_demo_users(self) -> List[User]:
        """Generate a list of demo users."""
        users = []
        
        # Regular users
        for i in range(20):
            username = f"user_{random.randint(1000, 9999)}"
            users.append(User(
                username=username,
                gender=random.choice(list(Gender)),
                has_tokens=random.choice([True, False]),
                is_mod=False,
                is_fan=random.choice([True, False]),
                tipped_recently=random.choice([True, False]),
                tipped_alot_recently=random.choice([True, False]) if random.random() > 0.7 else False,
                tipped_tons_recently=random.choice([True, False]) if random.random() > 0.9 else False
            ))
            
        # Add some mods
        for i in range(3):
            username = f"mod_{random.randint(100, 999)}"
            users.append(User(
                username=username,
                gender=random.choice(list(Gender)),
                has_tokens=True,
                is_mod=True,
                is_fan=True,
                tipped_recently=True,
                tipped_alot_recently=True,
                tipped_tons_recently=random.choice([True, False])
            ))
            
        # Add some big tippers
        for i in range(5):
            username = f"whale_{random.randint(100, 999)}"
            users.append(User(
                username=username,
                gender=random.choice(list(Gender)),
                has_tokens=True,
                is_mod=False,
                is_fan=True,
                tipped_recently=True,
                tipped_alot_recently=True,
                tipped_tons_recently=True
            ))
            
        return users
        
    def generate_random_user(self) -> User:
        """Generate a random user."""
        return random.choice(self.demo_users)
        
    def generate_tip_event(
        self, 
        room: str = "demo_room",
        broadcaster: str = "demo_broadcaster",
        timestamp: Optional[datetime] = None
    ) -> TipEvent:
        """Generate a random tip event."""
        user = self.generate_random_user()
        
        # Adjust token amount based on user type
        if user.tipped_tons_recently:
            tokens = random.randint(500, 5000)
        elif user.tipped_alot_recently:
            tokens = random.randint(100, 500)
        elif user.tipped_recently:
            tokens = random.randint(10, 100)
        else:
            tokens = random.randint(1, 50)
            
        message = random.choice(self.demo_messages) if random.random() > 0.3 else ""
        
        return TipEvent(
            timestamp=timestamp or datetime.utcnow(),
            room=room,
            broadcaster=broadcaster,
            user=user,
            tokens=tokens,
            message=message,
            is_anonymous=random.random() < 0.1  # 10% anonymous
        )
        
    def generate_message_event(
        self,
        room: str = "demo_room",
        broadcaster: str = "demo_broadcaster",
        timestamp: Optional[datetime] = None
    ) -> MessageEvent:
        """Generate a random chat message event."""
        user = self.generate_random_user()
        message = random.choice(self.demo_messages)
        
        # Mods might have colored messages
        color = None
        if user.is_mod and random.random() > 0.5:
            color = random.choice(["#FF0000", "#00FF00", "#0000FF", "#FFFF00"])
            
        return MessageEvent(
            timestamp=timestamp or datetime.utcnow(),
            room=room,
            broadcaster=broadcaster,
            user=user,
            message=message,
            color=color
        )
        
    def generate_join_event(
        self,
        room: str = "demo_room",
        broadcaster: str = "demo_broadcaster",
        timestamp: Optional[datetime] = None
    ) -> UserJoinEvent:
        """Generate a user join event."""
        user = self.generate_random_user()
        
        return UserJoinEvent(
            timestamp=timestamp or datetime.utcnow(),
            room=room,
            broadcaster=broadcaster,
            user=user
        )
        
    def generate_leave_event(
        self,
        room: str = "demo_room",
        broadcaster: str = "demo_broadcaster",
        timestamp: Optional[datetime] = None
    ) -> UserLeaveEvent:
        """Generate a user leave event."""
        user = self.generate_random_user()
        
        return UserLeaveEvent(
            timestamp=timestamp or datetime.utcnow(),
            room=room,
            broadcaster=broadcaster,
            user=user
        )
        
    def generate_media_purchase_event(
        self,
        room: str = "demo_room",
        broadcaster: str = "demo_broadcaster",
        timestamp: Optional[datetime] = None
    ) -> MediaPurchaseEvent:
        """Generate a media purchase event."""
        user = self.generate_random_user()
        
        media_types = ["photo_set", "video", "album", "snapchat"]
        media_names = [
            "Premium Photo Set #1",
            "Exclusive Video Collection",
            "Private Album Access",
            "Snapchat Lifetime Access",
            "Custom Video Request"
        ]
        
        tokens = random.choice([50, 100, 200, 500, 1000])
        
        return MediaPurchaseEvent(
            timestamp=timestamp or datetime.utcnow(),
            room=room,
            broadcaster=broadcaster,
            user=user,
            media_type=random.choice(media_types),
            media_name=random.choice(media_names),
            tokens=tokens
        )
        
    def generate_private_message_event(
        self,
        from_user: Optional[str] = None,
        to_user: str = "demo_broadcaster",
        room: str = "demo_room",
        broadcaster: str = "demo_broadcaster",
        timestamp: Optional[datetime] = None
    ) -> PrivateMessageEvent:
        """Generate a private message event."""
        if not from_user:
            user = self.generate_random_user()
            from_user = user.username
            
        private_messages = [
            "Hey, love your show!",
            "Can we do a private?",
            "You're amazing!",
            "Just sent you a big tip!",
            "Check out my request",
            "Thanks for the show!",
            "When's your next stream?",
            "You're my favorite!",
            "Can't wait to see more"
        ]
        
        return PrivateMessageEvent(
            timestamp=timestamp or datetime.utcnow(),
            room=room,
            broadcaster=broadcaster,
            from_user=from_user,
            to_user=to_user,
            message=random.choice(private_messages),
            tokens=random.choice([0, 1, 5, 10]) if random.random() > 0.5 else 0
        )
        
    def generate_event_stream(
        self,
        duration_minutes: int = 60,
        events_per_minute: int = 10,
        room: str = "demo_room",
        broadcaster: str = "demo_broadcaster"
    ) -> List[Any]:
        """Generate a stream of mixed events over time.
        
        Args:
            duration_minutes: Duration of the stream in minutes
            events_per_minute: Average events per minute
            room: Room name
            broadcaster: Broadcaster name
            
        Returns:
            List of events ordered by timestamp
        """
        events = []
        start_time = datetime.utcnow() - timedelta(minutes=duration_minutes)
        
        # Event type weights
        event_weights = {
            "message": 50,
            "tip": 20,
            "join": 15,
            "leave": 10,
            "media": 3,
            "private": 2
        }
        
        total_events = duration_minutes * events_per_minute
        
        for i in range(total_events):
            # Random timestamp within the duration
            offset_seconds = random.randint(0, duration_minutes * 60)
            timestamp = start_time + timedelta(seconds=offset_seconds)
            
            # Choose event type based on weights
            event_type = random.choices(
                list(event_weights.keys()),
                weights=list(event_weights.values())
            )[0]
            
            if event_type == "message":
                event = self.generate_message_event(room, broadcaster, timestamp)
            elif event_type == "tip":
                event = self.generate_tip_event(room, broadcaster, timestamp)
            elif event_type == "join":
                event = self.generate_join_event(room, broadcaster, timestamp)
            elif event_type == "leave":
                event = self.generate_leave_event(room, broadcaster, timestamp)
            elif event_type == "media":
                event = self.generate_media_purchase_event(room, broadcaster, timestamp)
            elif event_type == "private":
                event = self.generate_private_message_event(
                    room=room, broadcaster=broadcaster, timestamp=timestamp
                )
                
            events.append(event)
            
        # Sort by timestamp
        events.sort(key=lambda e: e.timestamp)
        
        return events