from flask import Flask
from routes.translate import bp as translate_bp
from client.es_client import load_mappings  # still works


def create_app() -> Flask:
    app = Flask(__name__)
    load_mappings()
    app.register_blueprint(translate_bp, url_prefix="/translate")
    return app

if __name__ == "__main__":
    # cd into server/ and run:
    create_app().run(debug=True)  # nosec B201 - Development only 