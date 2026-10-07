from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
from schemas import (
    LoginRequest, Token
)
from auth import (
    authenticate_user, create_access_token
)

router = APIRouter()



@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Аутентификация пользователя и получение JWT токена.
    Токен действителен 30 минут.
    """
    db_user = authenticate_user(db, login_data.username, login_data.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password", 
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    access_token = create_access_token(
        data={
            "sub": db_user.username,
            "is_admin": db_user.is_admin,
            "is_librarian": db_user.is_librarian
        },
        expires_delta=timedelta(minutes=30)
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }