from passlib.hash import pbkdf2_sha256

from app.secrets import SALT
from app.models.user import User, NewUser, UserPublic
from app.db.db import db


def create_user(user: NewUser):
    data = {
        'email': user.email,
        'password_digest': pbkdf2_sha256.hash(user.password + SALT)
    }
    return db.users.insert_one(data)


def get_user(email: str):
    user_data = db.users.find_one({'email': email})
    user_data['id'] = str(user_data['_id'])
    if user_data:
        return User(**user_data)


def get_all_users():
    def map_fun(user_data):
        user_data['id'] = str(user_data['_id'])
        return UserPublic(**user_data)

    return list(map(map_fun, db.users.find()))
