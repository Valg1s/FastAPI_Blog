from typing import Annotated

import jwt
from fastapi import HTTPException , Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from swetter.database.db import SessionLocal
from swetter import SECRET_KEY, ALGORITHM
from swetter.schem import TokenData
from swetter.models import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db=Depends(get_db)):
    '''
    Get the current user based on the provided token.
    This function decodes the JWT token to extract the username and retrieves the corresponding user from the database.
    :param token: JWT token
    :param db: db session
    :return: User object
    :raises HTTPException: If the token is invalid or user is not found
    '''

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError as e:
        print(e)
        raise credentials_exception

    user = User.get_user_by_username(db, token_data.username)

    if user is None:
        print("User not found")
        raise credentials_exception

    return user
