from flask_restx import Namespace, Resource, fields
from datetime import datetime, timedelta

from core.dependencies import get_event_repository
from utils.auth import requires_auth
from common.response_models import create_error_model, success_response
from common.error_handlers import ValidationError, NotFoundError

api = Namespace("chaturbate/events", description="Chaturbate event operations")

# Create response models
error_model = create_error_model(api)

event_stats_model = api.model(
    "EventStats",
    {
        "event_type": fields.String(description="Event type"),
        "count": fields.Integer(description="Number of events"),
    }
)

top_tipper_model = api.model(
    "TopTipper",
    {
        "username": fields.String(description="Username"),
        "total_tokens": fields.Integer(description="Total tokens tipped"),
    }
)

event_model = api.model(
    "Event",
    {
        "timestamp": fields.DateTime(description="Event timestamp"),
        "type": fields.String(description="Event type"),
        "username": fields.String(description="User who triggered the event"),
        "data": fields.Raw(description="Event-specific data"),
    }
)


@api.route("/<string:broadcaster>/stats")
class EventStats(Resource):
    @api.response(200, "Success")
    @api.response(400, "Bad Request", error_model)
    @api.response(401, "Unauthorized", error_model)
    @api.doc("get_event_stats")
    @requires_auth
    def get(self, broadcaster: str):
        """Get event statistics for a broadcaster."""
        repository = get_event_repository()
        if not repository:
            raise NotFoundError("Event tracking not available")
            
        # Get stats for last 24 hours by default
        start_time = datetime.utcnow() - timedelta(hours=24)
        
        try:
            event_counts = repository.get_event_counts_by_type(
                broadcaster=broadcaster,
                start=start_time
            )
            
            stats = [
                {"event_type": event_type, "count": count}
                for event_type, count in event_counts.items()
            ]
            
            return success_response(data={
                "broadcaster": broadcaster,
                "period": "24h",
                "stats": stats
            })
            
        except Exception as e:
            raise ValidationError(f"Failed to get event stats: {str(e)}")


@api.route("/<string:broadcaster>/top-tippers")
class TopTippers(Resource):
    @api.response(200, "Success")
    @api.response(400, "Bad Request", error_model)
    @api.response(401, "Unauthorized", error_model)
    @api.doc("get_top_tippers")
    @api.param("days", "Number of days to look back (default: 30)")
    @api.param("limit", "Number of top tippers to return (default: 10)")
    @requires_auth
    def get(self, broadcaster: str):
        """Get top tippers for a broadcaster."""
        from flask import request
        
        repository = get_event_repository()
        if not repository:
            raise NotFoundError("Event tracking not available")
            
        # Parse query parameters
        days = int(request.args.get("days", 30))
        limit = int(request.args.get("limit", 10))
        
        if days < 1 or days > 365:
            raise ValidationError("Days must be between 1 and 365")
            
        if limit < 1 or limit > 100:
            raise ValidationError("Limit must be between 1 and 100")
            
        start_time = datetime.utcnow() - timedelta(days=days)
        
        try:
            top_tippers = repository.get_top_tippers(
                broadcaster=broadcaster,
                start=start_time,
                limit=limit
            )
            
            tippers = [
                {
                    "username": tipper.get("username", "Unknown"),
                    "total_tokens": tipper.get("_value", 0)
                }
                for tipper in top_tippers
            ]
            
            return success_response(data={
                "broadcaster": broadcaster,
                "period": f"{days}d",
                "top_tippers": tippers
            })
            
        except Exception as e:
            raise ValidationError(f"Failed to get top tippers: {str(e)}")


@api.route("/<string:broadcaster>/user/<string:username>")
class UserActivity(Resource):
    @api.response(200, "Success")
    @api.response(400, "Bad Request", error_model)
    @api.response(401, "Unauthorized", error_model)
    @api.doc("get_user_activity")
    @api.param("days", "Number of days to look back (default: 7)")
    @requires_auth
    def get(self, broadcaster: str, username: str):
        """Get activity for a specific user in a broadcaster's room."""
        from flask import request
        
        repository = get_event_repository()
        if not repository:
            raise NotFoundError("Event tracking not available")
            
        days = int(request.args.get("days", 7))
        if days < 1 or days > 365:
            raise ValidationError("Days must be between 1 and 365")
            
        start_time = datetime.utcnow() - timedelta(days=days)
        
        try:
            activities = repository.get_user_activity(
                username=username,
                broadcaster=broadcaster,
                start=start_time
            )
            
            events = []
            for activity in activities:
                event = {
                    "timestamp": activity.get("_time"),
                    "type": activity.get("method", "unknown"),
                    "username": username,
                    "data": {}
                }
                
                # Extract relevant data based on event type
                if activity.get("method") == "tip":
                    event["data"]["tokens"] = activity.get("object.tip.tokens", 0)
                    event["data"]["message"] = activity.get("object.tip.message", "")
                elif activity.get("method") == "chatMessage":
                    event["data"]["message"] = activity.get("object.message.message", "")
                elif activity.get("method") == "mediaPurchase":
                    event["data"]["media_name"] = activity.get("object.media.name", "")
                    event["data"]["tokens"] = activity.get("object.media.tokens", 0)
                    
                events.append(event)
                
            return success_response(data={
                "broadcaster": broadcaster,
                "username": username,
                "period": f"{days}d",
                "events": events,
                "total_events": len(events)
            })
            
        except Exception as e:
            raise ValidationError(f"Failed to get user activity: {str(e)}")


@api.route("/<string:broadcaster>/recent")
class RecentEvents(Resource):
    @api.response(200, "Success")
    @api.response(400, "Bad Request", error_model)
    @api.response(401, "Unauthorized", error_model)
    @api.doc("get_recent_events")
    @api.param("minutes", "Number of minutes to look back (default: 60)")
    @api.param("event_type", "Filter by event type (optional)")
    @requires_auth
    def get(self, broadcaster: str):
        """Get recent events for a broadcaster."""
        from flask import request
        
        repository = get_event_repository()
        if not repository:
            raise NotFoundError("Event tracking not available")
            
        minutes = int(request.args.get("minutes", 60))
        event_type = request.args.get("event_type")
        
        if minutes < 1 or minutes > 1440:  # Max 24 hours
            raise ValidationError("Minutes must be between 1 and 1440")
            
        start_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        filters = {"broadcaster": broadcaster}
        if event_type:
            filters["method"] = event_type
            
        try:
            events = repository.find_by_time_range(
                start=start_time,
                filters=filters
            )
            
            # Limit to most recent 100 events
            events = events[:100]
            
            return success_response(data={
                "broadcaster": broadcaster,
                "period": f"{minutes}m",
                "event_type": event_type,
                "events": events,
                "count": len(events)
            })
            
        except Exception as e:
            raise ValidationError(f"Failed to get recent events: {str(e)}")