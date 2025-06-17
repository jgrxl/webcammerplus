import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional, TypeVar, Generic
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from utils.query_builder import FluxQueryBuilder

logger = logging.getLogger(__name__)

T = TypeVar('T')


class InfluxBaseRepository(ABC, Generic[T]):
    """Base repository for InfluxDB operations."""
    
    def __init__(self, client: InfluxDBClient, bucket: str, measurement: str):
        """Initialize the repository.
        
        Args:
            client: InfluxDB client instance
            bucket: The bucket to use
            measurement: The measurement name
        """
        self.client = client
        self.bucket = bucket
        self.measurement = measurement
        # Get the actual InfluxDB client from our wrapper
        if hasattr(client, 'client'):
            self.write_api = client.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = client.client.query_api()
        else:
            # Direct InfluxDB client
            self.write_api = client.write_api(write_options=SYNCHRONOUS)
            self.query_api = client.query_api()
        
    @abstractmethod
    def save(self, entity: T) -> bool:
        """Save an entity to InfluxDB.
        
        Args:
            entity: The entity to save
            
        Returns:
            True if successful, False otherwise
        """
        
    @abstractmethod
    def find_by_time_range(
        self, 
        start: datetime, 
        end: Optional[datetime] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """Find entities within a time range.
        
        Args:
            start: Start time
            end: End time (defaults to now)
            filters: Additional filters to apply
            
        Returns:
            List of entities
        """
        
    def write_point(self, point: Point) -> bool:
        """Write a point to InfluxDB.
        
        Args:
            point: The point to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.write_api.write(bucket=self.bucket, record=point)
            return True
        except Exception as e:
            logger.error(f"Failed to write point to InfluxDB: {e}")
            return False
            
    def write_points(self, points: List[Point]) -> bool:
        """Write multiple points to InfluxDB.
        
        Args:
            points: List of points to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.write_api.write(bucket=self.bucket, record=points)
            return True
        except Exception as e:
            logger.error(f"Failed to write points to InfluxDB: {e}")
            return False
            
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a Flux query.
        
        Args:
            query: The Flux query string
            
        Returns:
            List of result dictionaries
        """
        try:
            tables = self.query_api.query(query)
            results = []
            
            for table in tables:
                for record in table.records:
                    results.append(record.values)
                    
            return results
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            return []
            
    def build_time_range_query(
        self,
        start: datetime,
        end: Optional[datetime] = None,
        filters: Optional[Dict[str, str]] = None,
        fields: Optional[List[str]] = None
    ) -> str:
        """Build a time range query using FluxQueryBuilder.
        
        Args:
            start: Start time
            end: End time
            filters: Tag filters
            fields: Fields to select
            
        Returns:
            Flux query string
        """
        builder = FluxQueryBuilder(self.bucket)
        
        # Set time range
        if end:
            builder.range(start, end)
        else:
            builder.range(start)
            
        # Add measurement filter
        builder.filter("_measurement", self.measurement)
        
        # Add additional filters
        if filters:
            for key, value in filters.items():
                builder.filter(key, value)
                
        # Select specific fields
        if fields:
            field_filters = " or ".join([f'r._field == "{f}"' for f in fields])
            builder.filter_fn(f"(r) => {field_filters}")
            
        return builder.build()
        
    def count_by_time_range(
        self,
        start: datetime,
        end: Optional[datetime] = None,
        filters: Optional[Dict[str, str]] = None
    ) -> int:
        """Count records within a time range.
        
        Args:
            start: Start time
            end: End time
            filters: Additional filters
            
        Returns:
            Count of records
        """
        query = self.build_time_range_query(start, end, filters)
        query += "\n|> count()"
        
        results = self.execute_query(query)
        if results and "_value" in results[0]:
            return results[0]["_value"]
        return 0
        
    def aggregate_by_tag(
        self,
        start: datetime,
        end: Optional[datetime] = None,
        group_by: str = "username",
        aggregation: str = "count",
        filters: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Aggregate data by a tag.
        
        Args:
            start: Start time
            end: End time
            group_by: Tag to group by
            aggregation: Aggregation function (count, sum, mean, etc.)
            filters: Additional filters
            limit: Result limit
            
        Returns:
            List of aggregated results
        """
        query = self.build_time_range_query(start, end, filters)
        query += f'\n|> group(columns: ["{group_by}"])'
        query += f"\n|> {aggregation}()"
        query += '\n|> group()'
        query += '\n|> sort(columns: ["_value"], desc: true)'
        
        if limit:
            query += f"\n|> limit(n: {limit})"
            
        return self.execute_query(query)