from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id_, name, email):
        self.id = id_
        self.name = name
        self.email = email

    @staticmethod
    def get(user_id):
        user = User(
            id_="q28", name="TestUser", email="test@gmail.com"
        )
        return user