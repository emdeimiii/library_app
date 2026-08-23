from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class TypeBook(BaseModel):
    id: str
    title: str = Field(..., min_length=1, max_length=200, description="Краткое название книги")
    author: str
    year: int
    genre: str
    isAvailable: bool = Field(True, description="Статус выполнения")
    description: str

    @validator("title")
    def title_cannot_be_whitespace(cls, v):
        if not v.strip():
            raise ValueError("title must contain non-whitespace characters")
        return v
    
class BookHistoryItem(BaseModel):
    bookId: str
    takenAt: date
    returnedAt: Optional[date]= None


class TypeReader(BaseModel):
    id: str
    fullName: str
    email: str
    phone: str
    registrationDate : str
    booksHistory: List[BookHistoryItem]
    activeBooks: List[str]
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

    