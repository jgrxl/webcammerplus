import logging
import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from flask_socketio import SocketIO

from client.influx_client import InfluxDBClient

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    # Validate InfluxDB connection on startup (fail fast)
    logger.info("Checking InfluxDB connection...")
    try:
        influx_client = InfluxDBClient()
        logger.info("✅ InfluxDB connection successful")
    except Exception as e:
        logger.error(f"❌ InfluxDB connection failed: {e}")
        raise RuntimeError(f"InfluxDB is required but not properly configured: {e}")

    # Configure app for sessions (required for OAuth)
    app.secret_key = os.getenv(
        "FLASK_SECRET_KEY", "your-secret-key-change-in-production"
    )

    @app.route("/")
    def healthcheck():
        return {"status": "ok"}, 200

    api = Api(
        app,
        version="1.0",
        title="WebCammerPlus API",
        description="API for translation, text generation, and reply services powered by Novita AI",
        doc="/docs/",
        prefix="/api/v1",
    )

    # Import all routes
    from routes.auth_route import api as auth_ns
    from routes.auth_route import setup_auth_routes
    from routes.chaturbate_route import api as chaturbate_ns
    from routes.chaturbate_route import setup_socketio
    from routes.inbox_route import api as inbox_ns
    from routes.influx_route import api as influx_ns
    from routes.reply_route import api as reply_ns
    from routes.subscription_route import api as subscription_ns
    from routes.translate_route import api as translate_ns
    from routes.write_route import api as write_ns
    from utils.auth import setup_oauth

    api.add_namespace(chaturbate_ns)
    api.add_namespace(translate_ns)
    api.add_namespace(reply_ns)
    api.add_namespace(write_ns)
    api.add_namespace(influx_ns)
    api.add_namespace(auth_ns)
    api.add_namespace(subscription_ns)
    api.add_namespace(inbox_ns)

    # Setup OAuth and auth routes
    oauth, auth0 = setup_oauth(app)
    setup_auth_routes(app, auth0)

    # Setup SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
    setup_socketio(app, socketio)

    # Store socketio instance on app for access in other modules
    app.socketio = socketio

    return app


if __name__ == "__main__":
    app = create_app()
    app.socketio.run(
        app, debug=True, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True
    )  # nosec B201 - Development only
