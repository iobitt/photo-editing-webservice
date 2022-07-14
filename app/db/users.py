import secrets
import string
from passlib.hash import pbkdf2_sha256

from app.secrets import SALT, ADMIN_USERNAME, ADMIN_PASSWORD
from app.models.user import User, NewUser, UserPublic
from app.db.db import db


def generate_password(pass_len: int):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(pass_len))


def create_user(user: NewUser, admin=False):
    data = {
        'email': user.email,
        'password_digest': pbkdf2_sha256.hash(user.password + SALT),
        'admin': admin
    }
    return db.users.insert_one(data)


def get_user(email: str):
    user_data = db.users.find_one({'email': email})
    if not user_data:
        return
    user_data['id'] = str(user_data['_id'])
    if user_data:
        return User(**user_data)


def get_all_users():
    def map_fun(user_data):
        user_data['id'] = str(user_data['_id'])
        return UserPublic(**user_data)

    return list(map(map_fun, db.users.find()))


def create_admin(username, password):
    admin = get_user(username)
    if not admin:
        user = NewUser(email=username, password=password)
        create_user(user, admin=True)


create_admin(ADMIN_USERNAME, ADMIN_PASSWORD)
