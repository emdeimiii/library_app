from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class TypeBook(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=200, description="Название книги")
    author: str = Field(..., min_length=1, max_length=100)
    isbn: Optional[str] = Field(None, max_length=20)  
    year: Optional[int] = Field(None, ge=1000, le=2100, description="Год издания")
    genre: Optional[str] = Field(None, max_length=50)
    available_copies: int = Field(0, ge=0, description="Количество доступных копий")
    description: Optional[str] = Field("", max_length=1000)

    @validator("title")
    def title_cannot_be_whitespace(cls, v):
        if not v.strip():
            raise ValueError("title must contain non-whitespace characters")
        return v

    @validator("author")
    def author_cannot_be_whitespace(cls, v):
        if not v.strip():
            raise ValueError("author must contain non-whitespace characters")
        return v

    class Config:
        from_attributes = True


class BookCreate(BaseModel):

    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    isbn: Optional[str] = Field(None, max_length=20)
    year: Optional[int] = Field(None, ge=1000, le=2100)
    genre: Optional[str] = Field(None, max_length=50)
    available_copies: int = Field(0, ge=0)
    description: Optional[str] = Field("", max_length=1000)

    @validator("title")
    def title_cannot_be_whitespace(cls, v):
        if not v.strip():
            raise ValueError("title must contain non-whitespace characters")
        return v

    @validator("author")
    def author_cannot_be_whitespace(cls, v):
        if not v.strip():
            raise ValueError("author must contain non-whitespace characters")
        return v


class BookHistoryItem(BaseModel):
    book_id: int 
    taken_at: str
    returned_at: Optional[str] = None

    class Config:
        from_attributes = True


class TypeBookDetail(TypeBook):

    pass




class TypeReader(BaseModel):

    id: int 
    full_name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9\s\-\(\)]{10,20}$")
    registration_date: str 
    books_history: List[BookHistoryItem] = []

    @validator("full_name")
    def full_name_cannot_be_whitespace(cls, v):
        if not v.strip():
            raise ValueError("full_name must contain non-whitespace characters")
        return v

    class Config:
        from_attributes = True


class TypeReaderProfile(TypeReader):
    """Профиль читателя с активными книгами."""
    active_books: List[TypeBook] = []



class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    is_admin: bool = False
    is_librarian: bool = False


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    is_admin: Optional[bool] = None
    is_librarian: Optional[bool] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True



class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    is_admin: Optional[bool] = None
    is_librarian: Optional[bool] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=100)