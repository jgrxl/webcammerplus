"""Mock models for demo mode - simulates chaturbate_poller.models structure"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class User:
    """Mock User model"""

    username: str


@dataclass
class Tip:
    """Mock Tip model"""

    tokens: int
    message: str = ""


@dataclass
class Message:
    """Mock Message model"""

    user: User
    message: str


@dataclass
class Event:
    """Mock Event model"""

    object: Any
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
