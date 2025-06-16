from enum import Enum
from typing import Any, Dict, List, Optional, Union


class Operator(Enum):
    """Supported filter operators for Flux queries."""

    EQ = "=="
    NE = "!="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    CONTAINS = "contains"
    REGEX = "=~"


class AggregateFunction(Enum):
    """Supported aggregate functions for Flux queries."""

    SUM = "sum"
    COUNT = "count"
    MEAN = "mean"
    MIN = "min"
    MAX = "max"
    FIRST = "first"
    LAST = "last"


class FluxQueryBuilder:
    """Fluent API for building InfluxDB Flux queries.

    Example usage:
        query = (FluxQueryBuilder()
                .from_bucket("my-bucket")
                .range(start="-7d", stop="now()")
                .filter("_measurement", Operator.EQ, "temperature")
                .filter("location", Operator.EQ, "office")
                .aggregate(AggregateFunction.MEAN)
                .group_by(["location"])
                .sort("_time", desc=True)
                .limit(100)
                .build())
    """

    def __init__(self):
        self._bucket: Optional[str] = None
        self._range_start: Optional[str] = None
        self._range_stop: Optional[str] = None
        self._filters: List[str] = []
        self._measurements: List[str] = []
        self._fields: List[str] = []
        self._keep_columns: List[str] = []
        self._drop_columns: List[str] = []
        self._group_by_columns: List[str] = []
        self._aggregate_func: Optional[str] = None
        self._aggregate_column: str = "_value"
        self._sort_columns: List[str] = []
        self._sort_desc: bool = False
        self._limit_count: Optional[int] = None
        self._offset_count: Optional[int] = None
        self._custom_operations: List[str] = []

    def from_bucket(self, bucket: str) -> "FluxQueryBuilder":
        """Set the source bucket for the query.

        Args:
            bucket: The InfluxDB bucket name

        Returns:
            Self for method chaining
        """
        if not bucket or not bucket.strip():
            raise ValueError("Bucket name cannot be empty")
        self._bucket = bucket.strip()
        return self

    def range(self, start: str, stop: str = "now()") -> "FluxQueryBuilder":
        """Set the time range for the query.

        Args:
            start: Start time (e.g., "-7d", "2023-01-01T00:00:00Z")
            stop: Stop time (default: "now()")

        Returns:
            Self for method chaining
        """
        if not start or not start.strip():
            raise ValueError("Start time cannot be empty")
        self._range_start = start.strip()
        self._range_stop = stop.strip()
        return self

    def filter(
        self, field: str, operator: Union[Operator, str], value: Any
    ) -> "FluxQueryBuilder":
        """Add a filter condition to the query.

        Args:
            field: The field name to filter on
            operator: The comparison operator
            value: The value to compare against

        Returns:
            Self for method chaining
        """
        if not field or not field.strip():
            raise ValueError("Field name cannot be empty")

        op_str = operator.value if isinstance(operator, Operator) else str(operator)

        # Handle different value types
        if isinstance(value, str):
            value_str = f'"{value}"'
        elif isinstance(value, bool):
            value_str = "true" if value else "false"
        elif value is None:
            value_str = "null"
        else:
            value_str = str(value)

        # Special handling for contains and regex operators
        if op_str == "contains":
            filter_expr = f"contains(value: {value_str}, set: r.{field})"
        elif op_str == "=~":
            filter_expr = f"r.{field} {op_str} /{value}/"
        else:
            filter_expr = f"r.{field} {op_str} {value_str}"

        self._filters.append(f"|> filter(fn: (r) => {filter_expr})")
        return self

    def measurement(self, measurement: str) -> "FluxQueryBuilder":
        """Filter by measurement name.

        Args:
            measurement: The measurement name

        Returns:
            Self for method chaining
        """
        return self.filter("_measurement", Operator.EQ, measurement)

    def field(self, field: str) -> "FluxQueryBuilder":
        """Filter by field name.

        Args:
            field: The field name

        Returns:
            Self for method chaining
        """
        return self.filter("_field", Operator.EQ, field)

    def keep(self, columns: List[str]) -> "FluxQueryBuilder":
        """Keep only specified columns in the result.

        Args:
            columns: List of column names to keep

        Returns:
            Self for method chaining
        """
        if not columns:
            raise ValueError("Columns list cannot be empty")
        self._keep_columns = [col.strip() for col in columns if col.strip()]
        return self

    def drop(self, columns: List[str]) -> "FluxQueryBuilder":
        """Drop specified columns from the result.

        Args:
            columns: List of column names to drop

        Returns:
            Self for method chaining
        """
        if not columns:
            raise ValueError("Columns list cannot be empty")
        self._drop_columns = [col.strip() for col in columns if col.strip()]
        return self

    def group_by(self, columns: List[str]) -> "FluxQueryBuilder":
        """Group results by specified columns.

        Args:
            columns: List of column names to group by

        Returns:
            Self for method chaining
        """
        if not columns:
            raise ValueError("Columns list cannot be empty")
        self._group_by_columns = [col.strip() for col in columns if col.strip()]
        return self

    def aggregate(
        self, func: Union[AggregateFunction, str], column: str = "_value"
    ) -> "FluxQueryBuilder":
        """Apply an aggregate function to the data.

        Args:
            func: The aggregate function to apply
            column: The column to aggregate (default: "_value")

        Returns:
            Self for method chaining
        """
        func_str = func.value if isinstance(func, AggregateFunction) else str(func)
        self._aggregate_func = func_str
        self._aggregate_column = column
        return self

    def sort(
        self, columns: Union[str, List[str]], desc: bool = False
    ) -> "FluxQueryBuilder":
        """Sort results by specified columns.

        Args:
            columns: Column name or list of column names to sort by
            desc: Sort in descending order (default: False)

        Returns:
            Self for method chaining
        """
        if isinstance(columns, str):
            columns = [columns]

        if not columns:
            raise ValueError("Sort columns cannot be empty")

        self._sort_columns = [col.strip() for col in columns if col.strip()]
        self._sort_desc = desc
        return self

    def limit(self, count: int) -> "FluxQueryBuilder":
        """Limit the number of results returned.

        Args:
            count: Maximum number of results

        Returns:
            Self for method chaining
        """
        if count <= 0:
            raise ValueError("Limit count must be positive")
        self._limit_count = count
        return self

    def offset(self, count: int) -> "FluxQueryBuilder":
        """Skip the specified number of results.

        Args:
            count: Number of results to skip

        Returns:
            Self for method chaining
        """
        if count < 0:
            raise ValueError("Offset count cannot be negative")
        self._offset_count = count
        return self

    def custom(self, operation: str) -> "FluxQueryBuilder":
        """Add a custom Flux operation to the query.

        Args:
            operation: Custom Flux operation string

        Returns:
            Self for method chaining
        """
        if not operation or not operation.strip():
            raise ValueError("Custom operation cannot be empty")
        self._custom_operations.append(operation.strip())
        return self

    def build(self) -> str:
        """Build and return the final Flux query string.

        Returns:
            The complete Flux query as a string

        Raises:
            ValueError: If required components are missing
        """
        if not self._bucket:
            raise ValueError("Bucket must be specified using from_bucket()")

        query_parts = []

        # Start with bucket
        query_parts.append(f'from(bucket: "{self._bucket}")')

        # Add range if specified
        if self._range_start:
            range_part = f"|> range(start: {self._range_start}"
            if self._range_stop:
                range_part += f", stop: {self._range_stop}"
            range_part += ")"
            query_parts.append(range_part)

        # Add filters
        query_parts.extend(self._filters)

        # Add custom operations
        query_parts.extend([f"|> {op}" for op in self._custom_operations])

        # Add column operations
        if self._keep_columns:
            cols_str = ", ".join([f'"{col}"' for col in self._keep_columns])
            query_parts.append(f"|> keep(columns: [{cols_str}])")

        if self._drop_columns:
            cols_str = ", ".join([f'"{col}"' for col in self._drop_columns])
            query_parts.append(f"|> drop(columns: [{cols_str}])")

        # Add grouping
        if self._group_by_columns:
            cols_str = ", ".join([f'"{col}"' for col in self._group_by_columns])
            query_parts.append(f"|> group(columns: [{cols_str}])")

        # Add aggregation
        if self._aggregate_func:
            if self._aggregate_column != "_value":
                query_parts.append(
                    f'|> {self._aggregate_func}(column: "{self._aggregate_column}")'
                )
            else:
                query_parts.append(f"|> {self._aggregate_func}()")

        # Add sorting
        if self._sort_columns:
            cols_str = ", ".join([f'"{col}"' for col in self._sort_columns])
            desc_str = "desc: true" if self._sort_desc else "desc: false"
            query_parts.append(f"|> sort(columns: [{cols_str}], {desc_str})")

        # Add offset
        if self._offset_count is not None:
            query_parts.append(f"|> tail(n: -{self._offset_count})")

        # Add limit
        if self._limit_count is not None:
            query_parts.append(f"|> limit(n: {self._limit_count})")

        return "\n    ".join(query_parts)

    def __str__(self) -> str:
        """Return the built query string."""
        return self.build()


# Convenience factory functions
def from_bucket(bucket: str) -> FluxQueryBuilder:
    """Create a new QueryBuilder starting with a bucket."""
    return FluxQueryBuilder().from_bucket(bucket)


def query() -> FluxQueryBuilder:
    """Create a new empty QueryBuilder."""
    return FluxQueryBuilder()
