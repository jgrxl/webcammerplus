import logging
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from flask import abort, request
from flask_restx import Namespace, Resource, fields

from client.influx_client import InfluxDBClient
from services.influx_db_service import InfluxDBService

logger = logging.getLogger(__name__)


api = Namespace("influx", description="InfluxDB analytics operations")

# Search request model
search_request_model = api.model(
    "SearchRequest",
    {
        "filters": fields.Raw(
            description='Filter conditions. Simple: {"method": "tip"} or Complex: {"user": {"operator": "!=", "value": ""}}',
            example={"method": "tip", "user": {"operator": "!=", "value": ""}},
        ),
        "range": fields.Raw(
            description="Time range specification",
            example={"start": "-7d", "stop": "now()"},
        ),
        "fields": fields.List(
            fields.String,
            description="Fields to include in results",
            example=["_time", "_value", "method"],
        ),
        "measurement": fields.String(
            description="InfluxDB measurement name", default="chaturbate_events"
        ),
        "limit": fields.Integer(
            description="Maximum number of results", default=100, min=1, max=10000
        ),
        "sort_by": fields.String(description="Field to sort by", default="_time"),
        "sort_desc": fields.Boolean(
            description="Sort in descending order", default=True
        ),
    },
)

# Tips request model
tips_request_model = api.model(
    "TipsRequest",
    {
        "days": fields.Integer(
            description="Number of days to look back", default=7, min=1, max=365
        )
    },
)

# Top chatters request model
chatters_request_model = api.model(
    "ChattersRequest",
    {
        "days": fields.Integer(
            description="Number of days to look back", default=7, min=1, max=365
        ),
        "limit": fields.Integer(
            description="Maximum number of chatters to return",
            default=10,
            min=1,
            max=100,
        ),
    },
)

# Response models
search_response_model = api.model(
    "SearchResponse",
    {
        "success": fields.Boolean(description="Success status"),
        "data": fields.Raw(description="Query results"),
        "count": fields.Integer(description="Number of results returned"),
        "error": fields.String(description="Error message if failed"),
    },
)

tips_response_model = api.model(
    "TipsResponse",
    {
        "success": fields.Boolean(description="Success status"),
        "total_tokens": fields.Integer(description="Total tokens received"),
        "days": fields.Integer(description="Number of days queried"),
        "error": fields.String(description="Error message if failed"),
    },
)

chatter_count_model = api.model(
    "ChatterCount",
    {
        "username": fields.String(description="Username"),
        "count": fields.Integer(description="Message count"),
    },
)

chatters_response_model = api.model(
    "ChattersResponse",
    {
        "success": fields.Boolean(description="Success status"),
        "chatters": fields.List(
            fields.Nested(chatter_count_model), description="Top chatters list"
        ),
        "days": fields.Integer(description="Number of days queried"),
        "error": fields.String(description="Error message if failed"),
    },
)

error_model = api.model("Error", {"error": fields.String(description="Error message")})


@dataclass
class SearchRequest:
    filters: Optional[Dict[str, Any]] = None
    range: Optional[Dict[str, str]] = None
    fields: Optional[List[str]] = None
    measurement: str = "chaturbate_events"
    limit: int = 100
    sort_by: str = "_time"
    sort_desc: bool = True


@dataclass
class SearchResponse:
    success: bool
    data: List[Dict[str, Any]]
    count: int
    error: Optional[str] = None


def get_influx_service() -> InfluxDBService:
    """Get configured InfluxDB service instance."""
    try:
        client = InfluxDBClient()
        return InfluxDBService(client, client.bucket)
    except Exception as e:
        logger.error(f"InfluxDB connection failed: {str(e)}")
        abort(500, description=f"InfluxDB service unavailable: {str(e)}")


@api.route("/search")
class InfluxSearch(Resource):
    @api.expect(search_request_model)
    @api.response(200, "Success", search_response_model)
    @api.response(400, "Bad Request", error_model)
    @api.response(500, "Internal Server Error", error_model)
    @api.doc("search_influx_data")
    def post(self):
        """Execute custom search query on InfluxDB with filters, range, and sorting"""
        try:
            payload = request.get_json(force=True) or {}
            search_req = SearchRequest(**payload)

            service = get_influx_service()

            # Use service method to execute search
            result = service.execute_search_query(
                measurement=search_req.measurement,
                filters=search_req.filters,
                range_config=search_req.range,
                fields=search_req.fields,
                sort_by=search_req.sort_by,
                sort_desc=search_req.sort_desc,
                limit=search_req.limit,
            )

            return result

        except Exception as e:
            return (
                {"success": False, "data": [], "count": 0, "error": str(e)},
                500,
            )


@api.route("/tips")
class InfluxTips(Resource):
    @api.expect(tips_request_model)
    @api.response(200, "Success", tips_response_model)
    @api.response(400, "Bad Request", error_model)
    @api.response(500, "Internal Server Error", error_model)
    @api.doc("get_total_tips")
    def post(self):
        """Get total tips received in the specified time period"""
        try:
            payload = request.get_json(force=True) or {}
            days = payload.get("days", 7)

            service = get_influx_service()

            result = service.get_total_tips(days)
            return asdict(result)

        except Exception as e:
            return {
                "success": False,
                "total_tokens": 0,
                "days": payload.get("days", 7),
                "error": str(e),
            }


@api.route("/chatters")
class InfluxChatters(Resource):
    @api.expect(chatters_request_model)
    @api.response(200, "Success", chatters_response_model)
    @api.response(400, "Bad Request", error_model)
    @api.response(500, "Internal Server Error", error_model)
    @api.doc("get_top_chatters")
    def post(self):
        """Get top chatters by message count in the specified time period"""
        try:
            payload = request.get_json(force=True) or {}
            days = payload.get("days", 7)
            limit = payload.get("limit", 10)

            service = get_influx_service()

            result = service.get_top_chatters(days, limit)
            return asdict(result)

        except Exception as e:
            return {
                "success": False,
                "chatters": [],
                "days": payload.get("days", 7),
                "error": str(e),
            }


@api.route("/tippers")
class InfluxTopTippers(Resource):
    @api.expect(
        chatters_request_model
    )  # Reuse the same model as it has the same parameters
    @api.response(200, "Success", fields.Raw(description="Top tippers response"))
    @api.response(400, "Bad Request", error_model)
    @api.response(500, "Internal Server Error", error_model)
    @api.doc("get_top_tippers")
    def post(self):
        """Get top tippers by total tokens in the specified time period"""
        try:
            payload = request.get_json(force=True) or {}
            days = payload.get("days", 7)
            limit = payload.get("limit", 10)

            service = get_influx_service()

            result = service.get_top_tippers(days, limit)
            return asdict(result)

        except Exception as e:
            return {
                "success": False,
                "tippers": [],
                "days": payload.get("days", 7),
                "error": str(e),
            }
