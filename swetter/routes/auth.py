from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, HTTPException, Response, Depends
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext

from swetter import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from swetter.models import User
from swetter.schem import UserSchem, Token
from swetter.utils.deps import get_db

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db, username: str, password: str):
    '''
    Check if user exists on db and equals of hash passwords
    :param db: db session
    :param username: user username
    :param password: user password
    :return: User instance from db if user correct authenticated else False
    '''

    user = User.get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.user_password_hash):
        return False
    return user


def create_access_token(data: dict) -> str:
    '''
    Create token using jwt and user data
    :param data: username and password
    :return: access token
    '''

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/registration/")
async def create_user(form_data: UserSchem, db=Depends(get_db)):
    '''
    Create user, if not exists or return error
    :param form_data: username and password
    :param db: db session
    :return: Empty response with 201 status code or Exception if user exists
    '''

    username, password = form_data.dict().values()

    user = User.get_user_by_username(db, username)

    if user:
        raise HTTPException(400, headers={"Cannot create": "User with this name already exists"})

    User.create_user(db, username, get_password_hash(password))

    return Response(status_code=201)


@router.post("/login/", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    '''
    Log in user by username and password. Return token
    :param form_data: username and password
    :param db: db session
    :return: Token if user authenticated or Exception if incorrect username or password
    '''

    user = authenticate_user(db, form_data.username, form_data.password)

    if not user or not verify_password(form_data.password, user.user_password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.user_name}
    )

    return Token(access_token=access_token, token_type="bearer")
