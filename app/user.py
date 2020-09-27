from flask_login import UserMixin
import pymongo
from bson.objectid import ObjectId

myclient = pymongo.MongoClient("mongodb://nerv:9201/")
mydb = myclient["MAI_UCLA_DB"]
USER_DB = mydb["user"]

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
        print("getting user....")
        # Check if user is in db
        query = {'user_id': str(user_id)}
        result = USER_DB.find_one(query)
        if result is None:
            return None

        user = User(
            id_=result['user_id'], name=result['user_name'], email=result['user_email'], role=result['user_role']
        )

        return user


    @staticmethod
    def create(id_, name, email, role):
        USER_DB.insert_one({
            "user_id": str(id_),
            "user_name": str(name),
            "user_email": str(email),
            "user_role": int(role)
        })