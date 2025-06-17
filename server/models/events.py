from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class EventType(Enum):
    """Chaturbate event types."""
    JOIN = "join"
    LEAVE = "leave"
    TIP = "tip"
    MESSAGE = "message"
    PRIVATE_MESSAGE = "private_message"
    ROOM_UPDATE = "room_update"
    BROADCASTER_UPDATE = "broadcaster_update"
    MEDIA_PURCHASE = "media_purchase"
    FOLLOW = "follow"
    UNFOLLOW = "unfollow"


class Gender(Enum):
    """User gender options."""
    MALE = "m"
    FEMALE = "f"
    TRANS = "t"
    COUPLE = "c"
    UNKNOWN = "unknown"


@dataclass
class BaseEvent:
    """Base class for all Chaturbate events."""
    event_type: EventType
    timestamp: datetime
    room: str
    broadcaster: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "room": self.room,
            "broadcaster": self.broadcaster
        }


@dataclass
class User:
    """Chaturbate user information."""
    username: str
    gender: Gender = Gender.UNKNOWN
    is_mod: bool = False
    is_fan: bool = False
    has_tokens: bool = False
    tipped_recently: bool = False
    tipped_alot_recently: bool = False
    tipped_tons_recently: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Create User from dictionary."""
        return cls(
            username=data.get("username", ""),
            gender=Gender(data.get("gender", "unknown")),
            is_mod=data.get("is_mod", False),
            is_fan=data.get("is_fan", False),
            has_tokens=data.get("has_tokens", False),
            tipped_recently=data.get("tipped_recently", False),
            tipped_alot_recently=data.get("tipped_alot_recently", False),
            tipped_tons_recently=data.get("tipped_tons_recently", False)
        )


@dataclass
class TipEvent(BaseEvent):
    """Tip event."""
    user: User
    tokens: int
    message: str = ""
    is_anonymous: bool = False
    
    def __post_init__(self):
        self.event_type = EventType.TIP
    
    def to_influx_point(self) -> Dict[str, Any]:
        """Convert to InfluxDB point format."""
        return {
            "measurement": "chaturbate_events",
            "tags": {
                "username": self.user.username,
                "broadcaster": self.broadcaster,
                "room": self.room,
                "method": "tip",
                "gender": self.user.gender.value,
                "is_anonymous": str(self.is_anonymous)
            },
            "fields": {
                "object.tip.tokens": self.tokens,
                "object.tip.message": self.message,
                "object.tip.is_anonymous": self.is_anonymous,
                "user.is_mod": self.user.is_mod,
                "user.has_tokens": self.user.has_tokens
            },
            "time": self.timestamp
        }


@dataclass
class MessageEvent(BaseEvent):
    """Chat message event."""
    user: User
    message: str
    color: Optional[str] = None
    font: Optional[str] = None
    
    def __post_init__(self):
        self.event_type = EventType.MESSAGE
    
    def to_influx_point(self) -> Dict[str, Any]:
        """Convert to InfluxDB point format."""
        return {
            "measurement": "chaturbate_events",
            "tags": {
                "username": self.user.username,
                "broadcaster": self.broadcaster,
                "room": self.room,
                "method": "chatMessage",
                "gender": self.user.gender.value
            },
            "fields": {
                "object.message.message": self.message,
                "object.message.color": self.color or "",
                "object.message.font": self.font or "",
                "user.is_mod": self.user.is_mod,
                "user.has_tokens": self.user.has_tokens
            },
            "time": self.timestamp
        }


@dataclass
class PrivateMessageEvent(BaseEvent):
    """Private message event."""
    from_user: str
    to_user: str
    message: str
    tokens: int = 0
    
    def __post_init__(self):
        self.event_type = EventType.PRIVATE_MESSAGE
    
    def to_influx_point(self) -> Dict[str, Any]:
        """Convert to InfluxDB point format."""
        return {
            "measurement": "private_messages",
            "tags": {
                "from_user": self.from_user,
                "to_user": self.to_user,
                "broadcaster": self.broadcaster,
                "room": self.room
            },
            "fields": {
                "message": self.message,
                "tokens": self.tokens
            },
            "time": self.timestamp
        }


@dataclass
class UserJoinEvent(BaseEvent):
    """User join event."""
    user: User
    
    def __post_init__(self):
        self.event_type = EventType.JOIN
    
    def to_influx_point(self) -> Dict[str, Any]:
        """Convert to InfluxDB point format."""
        return {
            "measurement": "chaturbate_events",
            "tags": {
                "username": self.user.username,
                "broadcaster": self.broadcaster,
                "room": self.room,
                "method": "userJoin",
                "gender": self.user.gender.value
            },
            "fields": {
                "user.is_mod": self.user.is_mod,
                "user.has_tokens": self.user.has_tokens,
                "user.is_fan": self.user.is_fan
            },
            "time": self.timestamp
        }


@dataclass
class UserLeaveEvent(BaseEvent):
    """User leave event."""
    user: User
    
    def __post_init__(self):
        self.event_type = EventType.LEAVE
    
    def to_influx_point(self) -> Dict[str, Any]:
        """Convert to InfluxDB point format."""
        return {
            "measurement": "chaturbate_events",
            "tags": {
                "username": self.user.username,
                "broadcaster": self.broadcaster,
                "room": self.room,
                "method": "userLeave",
                "gender": self.user.gender.value
            },
            "fields": {
                "user.is_mod": self.user.is_mod,
                "user.has_tokens": self.user.has_tokens,
                "user.is_fan": self.user.is_fan
            },
            "time": self.timestamp
        }


@dataclass
class MediaPurchaseEvent(BaseEvent):
    """Media purchase event."""
    user: User
    media_type: str
    media_name: str
    tokens: int
    
    def __post_init__(self):
        self.event_type = EventType.MEDIA_PURCHASE
    
    def to_influx_point(self) -> Dict[str, Any]:
        """Convert to InfluxDB point format."""
        return {
            "measurement": "chaturbate_events",
            "tags": {
                "username": self.user.username,
                "broadcaster": self.broadcaster,
                "room": self.room,
                "method": "mediaPurchase",
                "media_type": self.media_type
            },
            "fields": {
                "object.media.name": self.media_name,
                "object.media.tokens": self.tokens,
                "user.is_mod": self.user.is_mod,
                "user.has_tokens": self.user.has_tokens
            },
            "time": self.timestamp
        }