from flask_login import UserMixin
from .database import db_interface as database

# ROLE BREAKDOWN:
#   00 = guest
#   05 = member
#   10 = admin

class User(UserMixin):
    def __init__(self, id_, name, email, role, picture):
        self.id = id_
        self.name = name
        self.email = email
        self.role = role
        self.picture = picture

    @staticmethod
    def get(user_id):
        # Check if user is in db
        if not database.exists_user_id(user_id):
            return None
        
        # Confirmed user is in db. Pull data
        result = database.get_user(user_id)

        return User(
            id_=result['user_id'], name=result['user_name'], email=result['user_email'], role=result['user_role'], picture=result['user_picture']
        )

    @staticmethod
    def create(id_, name, email, role, picture):
        database.insert_user(id_, name, email, role, picture)