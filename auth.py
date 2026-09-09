
from pwdlib import PasswordHash
from datetime import datetime, timedelta
from database import get_db
from models import User
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from math import dist
import settings
from fastapi import HTTPException, Request, status, Depends

pwd_context = PasswordHash.recommended()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_accsess_token(data: dist, expires_delta: timedelta = 30) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({'exp': expire})
    encode_jwt= jwt.encode(
        to_encode, settings.SECRET_KEY, settings.ALGORYTM
    )
    return encode_jwt

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def get_token(request:Request):
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer"):
            token = auth_header[8:]
    print(token)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    return token

def get_current_user(token: str = Depends(get_token), db: Session = Depends(get_db)):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORYTM)
            username = payload.get('sub')
            if not username:
                 raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token does not contain user info')
        except JWTError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Token')
        user = get_user(db, username)
        if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
        return user

def get_admin_user(cur_user: User = Depends(get_current_user)):
     if not cur_user.is_admin:
          raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED, detail='Нужны права администратора'
         )
     return cur_user

def get_librarian_user(cur_user: User = Depends(get_current_user)):
     if not cur_user.is_admin:
          raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED, detail='Нужны права библиотекаря'
         )
     return cur_user

def get_current_active_user(current_user: User = Depends(get_current_user)):
     if not current_user.is_active:
                    raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED, detail='Пользователь неактивен'
         )
     return current_user
     