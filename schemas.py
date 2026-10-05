from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class TypeBook(BaseModel):
    id: str
    title: str = Field(..., min_length=1, max_length=200, description="Краткое название книги")
    author: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1000, le=2100, description="Год издания")
    genre: str = Field(..., min_length=1, max_length=50)
    isAvailable: bool = Field(True, description="Статус доступности")
    description: str = Field("", max_length=1000)

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
    bookId: str
    takenAt: date
    returnedAt: Optional[date] = None


class TypeReader(BaseModel):
    id: str
    fullName: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?[0-9\s\-\(\)]{10,20}$")
    registrationDate: date  # ✅ Исправлено: было str
    booksHistory: List[BookHistoryItem] = []
    activeBooks: List[str] = []

    @validator("fullName")
    def fullName_cannot_be_whitespace(cls, v):
        if not v.strip():
            raise ValueError("fullName must contain non-whitespace characters")
        return v


class TypeReaderProfile(TypeReader):
    reading_history: Optional[List[TypeBook]] = None


class TypeBookDetail(TypeBook):
    is_available: bool = Field(True, description="Статус доступности")
    reader_name: Optional[str] = None


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    # Булевы поля ролей
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
    reader_id: Optional[int] = None

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