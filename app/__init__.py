# app/__init__.py

from flask import Flask
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from .user import User

import os

# Initialize the app
app = Flask(__name__, instance_relative_config=True)
app.secret_key = os.environ.get("MAI_SECRET_KEY") or os.urandom(24)

GOOGLE_CLIENT_ID = os.environ.get("MAI_GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("MAI_GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Auth
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Load the views
from app import views

# Load the config file
app.config.from_object('config')
