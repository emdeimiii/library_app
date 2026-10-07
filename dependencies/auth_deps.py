from auth import decode_access_token, get_user
from database import get_db
from models import User
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi import HTTPException, Request, status, Depends



def get_token(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token not found'
        )
    return token


def get_current_user(
    token: str = Depends(get_token),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User is inactive'
        )
    return current_user


def get_admin_user(
    cur_user: User = Depends(get_current_active_user)
) -> User:
    if not cur_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Нужны права администратора'
        )
    return cur_user


def get_librarian_user(
    cur_user: User = Depends(get_current_active_user)
) -> User:

    if not (cur_user.is_librarian or cur_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Librarian access required'
        )
    return cur_user