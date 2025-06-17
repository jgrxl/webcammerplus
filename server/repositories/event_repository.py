import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from influxdb_client import InfluxDBClient, Point
from models.events import (
    BaseEvent
)
from .influx_base_repository import InfluxBaseRepository

logger = logging.getLogger(__name__)


class EventRepository(InfluxBaseRepository[BaseEvent]):
    """Repository for Chaturbate events."""
    
    def __init__(self, client: InfluxDBClient, bucket: str = "webcammerplus"):
        super().__init__(client, bucket, "chaturbate_events")
        
    def save(self, entity: BaseEvent) -> bool:
        """Save an event to InfluxDB.
        
        Args:
            entity: The event to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            point_data = entity.to_influx_point()
            point = Point(point_data["measurement"])
            
            # Add tags
            for key, value in point_data["tags"].items():
                point.tag(key, value)
                
            # Add fields
            for key, value in point_data["fields"].items():
                point.field(key, value)
                
            # Set timestamp
            point.time(point_data["time"])
            
            return self.write_point(point)
            
        except Exception as e:
            logger.error(f"Failed to save event: {e}")
            return False
            
    def save_batch(self, events: List[BaseEvent]) -> bool:
        """Save multiple events to InfluxDB.
        
        Args:
            events: List of events to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            points = []
            for event in events:
                point_data = event.to_influx_point()
                point = Point(point_data["measurement"])
                
                for key, value in point_data["tags"].items():
                    point.tag(key, value)
                    
                for key, value in point_data["fields"].items():
                    point.field(key, value)
                    
                point.time(point_data["time"])
                points.append(point)
                
            return self.write_points(points)
            
        except Exception as e:
            logger.error(f"Failed to save batch of events: {e}")
            return False
            
    def find_by_time_range(
        self,
        start: datetime,
        end: Optional[datetime] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[BaseEvent]:
        """Find events within a time range.
        
        Note: This returns raw data, not event objects, due to InfluxDB's nature.
        Use specific query methods for typed results.
        """
        query = self.build_time_range_query(start, end, filters)
        return self.execute_query(query)
        
    def find_tips(
        self,
        broadcaster: str,
        start: datetime,
        end: Optional[datetime] = None,
        min_tokens: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Find tip events for a broadcaster.
        
        Args:
            broadcaster: The broadcaster's username
            start: Start time
            end: End time
            min_tokens: Minimum token amount
            limit: Result limit
            
        Returns:
            List of tip data
        """
        filters = {
            "broadcaster": broadcaster,
            "method": "tip"
        }
        
        query = self.build_time_range_query(start, end, filters)
        
        if min_tokens:
            query += f'\n|> filter(fn: (r) => r._field == "object.tip.tokens" and r._value >= {min_tokens})'
            
        query += '\n|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
        query += '\n|> sort(columns: ["_time"], desc: true)'
        
        if limit:
            query += f"\n|> limit(n: {limit})"
            
        return self.execute_query(query)
        
    def find_messages(
        self,
        broadcaster: str,
        start: datetime,
        end: Optional[datetime] = None,
        username: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Find chat messages for a broadcaster.
        
        Args:
            broadcaster: The broadcaster's username
            start: Start time
            end: End time
            username: Filter by specific user
            limit: Result limit
            
        Returns:
            List of message data
        """
        filters = {
            "broadcaster": broadcaster,
            "method": "chatMessage"
        }
        
        if username:
            filters["username"] = username
            
        query = self.build_time_range_query(start, end, filters)
        query += '\n|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
        query += '\n|> sort(columns: ["_time"], desc: true)'
        
        if limit:
            query += f"\n|> limit(n: {limit})"
            
        return self.execute_query(query)
        
    def get_top_tippers(
        self,
        broadcaster: str,
        start: datetime,
        end: Optional[datetime] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top tippers for a broadcaster.
        
        Args:
            broadcaster: The broadcaster's username
            start: Start time
            end: End time
            limit: Number of top tippers
            
        Returns:
            List of top tippers with total tokens
        """
        filters = {
            "broadcaster": broadcaster,
            "method": "tip"
        }
        
        query = self.build_time_range_query(
            start, end, filters, 
            fields=["object.tip.tokens"]
        )
        query += '\n|> group(columns: ["username"])'
        query += '\n|> sum(column: "_value")'
        query += '\n|> group()'
        query += '\n|> sort(columns: ["_value"], desc: true)'
        query += f'\n|> limit(n: {limit})'
        
        return self.execute_query(query)
        
    def get_event_counts_by_type(
        self,
        broadcaster: str,
        start: datetime,
        end: Optional[datetime] = None
    ) -> Dict[str, int]:
        """Get event counts grouped by type.
        
        Args:
            broadcaster: The broadcaster's username
            start: Start time
            end: End time
            
        Returns:
            Dictionary of event type to count
        """
        filters = {"broadcaster": broadcaster}
        
        query = self.build_time_range_query(start, end, filters)
        query += '\n|> group(columns: ["method"])'
        query += '\n|> count()'
        
        results = self.execute_query(query)
        
        counts = {}
        for result in results:
            method = result.get("method", "unknown")
            count = result.get("_value", 0)
            counts[method] = count
            
        return counts
        
    def get_user_activity(
        self,
        username: str,
        broadcaster: str,
        start: datetime,
        end: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get all activity for a specific user.
        
        Args:
            username: The user's username
            broadcaster: The broadcaster's username
            start: Start time
            end: End time
            
        Returns:
            List of user activities
        """
        filters = {
            "username": username,
            "broadcaster": broadcaster
        }
        
        query = self.build_time_range_query(start, end, filters)
        query += '\n|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
        query += '\n|> sort(columns: ["_time"], desc: true)'
        
        return self.execute_query(query)