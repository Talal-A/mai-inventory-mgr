# app/__init__.py

from flask import Flask

# Initialize the app
app = Flask(__name__, instance_relative_config=True)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Load the views
from app import views

# Load the config file
app.config.from_object('config')
