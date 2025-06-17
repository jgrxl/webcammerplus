import logging

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from flask_socketio import SocketIO

from client.influx_client import InfluxDBClient
from common.error_handlers import register_error_handlers
from config import get_config
from core.dependencies import get_container, set_socketio

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
config = get_config()


def create_app() -> Flask:
    app = Flask(__name__)

    # Configure from centralized config
    app.config.update(
        SECRET_KEY=config.app.secret_key, DEBUG=config.app.debug, ENV=config.environment
    )

    # Configure CORS
    CORS(app, origins=config.app.cors_origins)

    # Configure logging
    logging.basicConfig(level=getattr(logging, config.app.log_level))

    # Register error handlers
    register_error_handlers(app)

    # Validate InfluxDB connection on startup (fail fast)
    logger.info("Checking InfluxDB connection...")
    try:
        InfluxDBClient()
        logger.info("✅ InfluxDB connection successful")
    except Exception as e:
        logger.error(f"❌ InfluxDB connection failed: {e}")
        raise RuntimeError(f"InfluxDB is required but not properly configured: {e}")

    @app.route("/")
    def healthcheck():
        return {"status": "ok"}, 200

    # Add health check at API root as well
    @app.route("/api/v1")
    @app.route("/api/v1/")
    def api_healthcheck():
        return {
            "status": "ok",
            "api_version": "1.0",
            "docs_url": "/docs/"
        }, 200

    api = Api(
        app,
        version="1.0",
        title="WebCammerPlus API",
        description="API for translation, text generation, and reply services powered by Novita AI",
        doc="/docs/",
        prefix="/api/v1",
    )

    # Initialize dependency container
    get_container()
    
    # Import all routes
    from routes.auth_route import api as auth_ns
    from routes.auth_route import setup_auth_routes
    from routes.chaturbate_route import api as chaturbate_ns
    from routes.chaturbate_route import setup_socketio
    from routes.chaturbate_events_route import api as events_ns
    from routes.inbox_route import api as inbox_ns
    from routes.influx_route import api as influx_ns
    from routes.reply_route import api as reply_ns
    from routes.subscription_route import api as subscription_ns
    from routes.translate_route import api as translate_ns
    from routes.user_stats_route import api as user_stats_ns
    from routes.write_route import api as write_ns
    from utils.auth import setup_oauth

    api.add_namespace(chaturbate_ns)
    api.add_namespace(events_ns)
    api.add_namespace(translate_ns)
    api.add_namespace(reply_ns)
    api.add_namespace(write_ns)
    api.add_namespace(influx_ns)
    api.add_namespace(auth_ns)
    api.add_namespace(subscription_ns)
    api.add_namespace(inbox_ns)
    api.add_namespace(user_stats_ns)

    # Setup OAuth and auth routes
    oauth, auth0 = setup_oauth(app)
    setup_auth_routes(app, auth0)

    # Setup SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
    setup_socketio(app, socketio)
    set_socketio(socketio)
    
    # Register new modular WebSocket handlers
    from handlers.chaturbate_websocket import register_websocket_handlers
    register_websocket_handlers(socketio)

    # Store socketio instance on app for access in other modules
    app.socketio = socketio

    return app


if __name__ == "__main__":
    app = create_app()
    app.socketio.run(
        app, debug=True, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True
    )  # nosec B201 - Development only
