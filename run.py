from flask import Flask
from flask_cors import CORS
from app.api import api

def create_app():
    app = Flask(__name__)
    CORS(app)  # ✅ Enable CORS globally
    app.register_blueprint(api, url_prefix="/api")
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
