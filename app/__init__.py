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

class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get('HTTP_X_FORWARDED_PROTO')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

# Initialize the app
app = Flask(__name__, instance_relative_config=True)
app.secret_key = os.environ.get("MAI_SECRET_KEY") or os.urandom(24)
app.wsgi_app = ReverseProxied(app.wsgi_app)

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
