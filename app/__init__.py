from flask import Flask
from .routes import register_routes

def create_app():
    app = Flask(__name__)
    from .utils import get_base_dir
    app.config['BASE_DIR'] = get_base_dir()
    app.config['UPLOAD_FOLDER'] = app.config['BASE_DIR']
    register_routes(app)
    return app
