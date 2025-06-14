from flask import Flask
from flask_cors import CORS
from flask_restx import Api
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)
    
    # Configure app for sessions (required for OAuth)
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-in-production')
    
    @app.route("/")
    def healthcheck():
        return {"status": "ok"}, 200
    
    api = Api(
        app,
        version='1.0',
        title='WebCammerPlus API',
        description='API for translation, text generation, and reply services powered by Novita AI',
        doc='/docs/',
        prefix='/api/v1'
    )
    
    from routes.translate_route import api as translate_ns
    from routes.reply_route import api as reply_ns
    from routes.write_route import api as write_ns
    from routes.influx_route import api as influx_ns
    from routes.auth_route import api as auth_ns, setup_auth_routes
    from routes.subscription_route import api as subscription_ns
    from utils.auth import setup_oauth
    
    api.add_namespace(translate_ns)
    api.add_namespace(reply_ns)
    api.add_namespace(write_ns)
    api.add_namespace(influx_ns)
    api.add_namespace(auth_ns)
    api.add_namespace(subscription_ns)
    
    # Setup OAuth and auth routes
    oauth, auth0 = setup_oauth(app)
    setup_auth_routes(app, auth0)
    
    return app


if __name__ == "__main__":
    create_app().run(debug=True)  # nosec B201 - Development only