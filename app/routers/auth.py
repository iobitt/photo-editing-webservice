from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.secrets import SECRET_KEY, SALT
from app.models.token import Token
from app.db.auth import authenticate_user, create_access_token
from app.db.users import get_user


PREFIX = '/auth'

router = APIRouter(
    prefix=PREFIX,
    tags=['auth'],
    responses={404: {"description": "Not found"}},
)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    user = authenticate_user(user, form_data.password, SALT)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email}, secret_key=SECRET_KEY)
    return {"access_token": access_token, "token_type": "bearer"}
