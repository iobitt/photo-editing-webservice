from typing import List

import pymongo.errors
from fastapi import APIRouter, Depends
from pymongo.errors import DuplicateKeyError

from app.dependencies import get_current_user
from app.models.user import NewUser, User
from app.db.users import get_all_users, create_user, generate_password


PREFIX = '/users'

router = APIRouter(
    prefix=PREFIX,
    dependencies=[Depends(get_current_user)],
    tags=['users'],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def index(current_user: User = Depends(get_current_user)):
    if not current_user.admin:
        return {'ok': False, 'error': 'Нет доступа'}

    return get_all_users()


@router.post("/")
async def create(user: NewUser, current_user: User = Depends(get_current_user)):
    if not current_user.admin:
        return {'ok': False, 'error': 'Нет доступа'}

    try:
        user = create_user(user)
        return {'ok': True, 'user_id': str(user.inserted_id)}
    except DuplicateKeyError:
        return {'ok': False, 'error': 'email занят'}


@router.post("/create_many")
async def create_many(users: List[NewUser], current_user: User = Depends(get_current_user)):
    if not current_user.admin:
        return {'ok': False, 'error': 'Нет доступа'}

    created_users = []
    for user_data in users:
        try:
            user_data.password = generate_password(12)
            create_user(user_data)
            created_users.append({'email': user_data.email, 'password': user_data.password})
        except pymongo.errors.DuplicateKeyError:
            created_users.append({'email': user_data.email, 'error': 'Имя пользователя занято'})
    return {'ok': True, 'users': created_users}
