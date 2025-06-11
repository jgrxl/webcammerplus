from flask import Flask
from routes.routes import bp as api_bp
from client.es_client import load_mappings   # still works

def create_app():
    app = Flask(__name__)
    load_mappings()
    app.register_blueprint(api_bp, url_prefix="/")
    @app.route("/")
    def hello(): return "Hello, World!"
    return app

if __name__=="__main__":
    # cd into server/ and run:
    create_app().run(debug=True)
