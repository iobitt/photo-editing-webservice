from fastapi import APIRouter, Depends
from pymongo.errors import DuplicateKeyError

from app.dependencies import get_current_user
from app.models.user import NewUser
from app.db.users import get_all_users, create_user


PREFIX = '/users'

router = APIRouter(
    prefix=PREFIX,
    dependencies=[Depends(get_current_user)],
    tags=['users'],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def index():
    return get_all_users()


@router.post("/")
async def create(user: NewUser):
    try:
        user = create_user(user)
        return {'ok': True, 'user_id': str(user.inserted_id)}
    except DuplicateKeyError:
        return {'ok': False, 'error': 'email занят'}
