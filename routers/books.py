from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, Book
from schemas import (
    TypeBook, TypeBookDetail)
from auth import ( get_admin_user,
    get_librarian_user
)
router = APIRouter()

@router.get("/books", response_model=List[TypeBook])
def get_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получение списка всех книг."""
    return db.query(Book).offset(skip).limit(limit).all()


@router.get("/books/{book_id}", response_model=TypeBookDetail)
def get_book(book_id: str, db: Session = Depends(get_db)):
    """Получение книги по ID."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/books", response_model=TypeBook, status_code=201)
def create_book(
    book_data: TypeBook,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """Создание новой книги. Доступно библиотекарям и админам."""
    if db.query(Book).filter(Book.id == book_data.id).first():
        raise HTTPException(status_code=400, detail="Book ID already exists")
    
    new_book = Book(**book_data.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@router.put("/books/{book_id}", response_model=TypeBook)
def update_book(
    book_id: str,
    book_data: TypeBook,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """Обновление книги. Доступно библиотекарям и админам."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    for key, value in book_data.dict().items():
        setattr(book, key, value)
    
    db.commit()
    db.refresh(book)
    return book


@router.delete("/books/{book_id}")
def delete_book(
    book_id: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Удаление книги. Доступно только админам."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully"}

