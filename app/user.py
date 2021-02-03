from flask_login import UserMixin
from . import database

# ROLE BREAKDOWN:
#   00 = guest
#   05 = member
#   10 = admin

class User(UserMixin):
    def __init__(self, id_, name, email, role):
        self.id = id_
        self.name = name
        self.email = email
        self.role = role

    @staticmethod
    def get(user_id):
        # Check if user is in db
        if not database.exists_user_id(user_id):
            return None
        
        # Confirmed user is in db. Pull data
        result = database.get_user(user_id)

        return User(
            id_=result['user_id'], name=result['user_name'], email=result['user_email'], role=result['user_role']
        )

    @staticmethod
    def create(id_, name, email, role):
        database.insert_user(id_, name, email, role)