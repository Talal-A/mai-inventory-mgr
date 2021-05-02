from flask_login import current_user
from app.database import db_interface as database

# Auth util

def validate_user():
    return current_user.is_authenticated and current_user.role >= 5

def validate_admin():
    return current_user.is_authenticated and current_user.role >= 10

def returnPermissionError():
    database.insert_history("PERMISSION_ERROR", current_user, "Attempted to access an unauthorized resource.")
    return "Error: you do not have permission to access this resource.", 401
