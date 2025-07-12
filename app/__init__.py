from flask import Flask
from .routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config['BASE_DIR'] = "/sdcard/Share"
    app.config['UPLOAD_FOLDER'] = app.config['BASE_DIR']
    register_routes(app)
    return app
