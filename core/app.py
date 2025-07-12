from flask import Flask
import os
from .routes import register_routes

BASE_DIR = '/sdcard/Share'
TEMPLATE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = TEMPLATE_DIR

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config['UPLOAD_FOLDER'] = BASE_DIR

register_routes(app)
