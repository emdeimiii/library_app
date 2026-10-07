from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import User, Book
from schemas import (
    BookCreate, TypeBook, TypeBookDetail)
from auth import ( get_admin_user,
    get_librarian_user
)
router = APIRouter()

@router.get("/books/search", response_model=List[TypeBook])
def search_books(
    title: Optional[str] = Query(None, description="Поиск по названию"),
    author: Optional[str] = Query(None, description="Поиск по автору"),
    db: Session = Depends(get_db)
):
    """
    Поиск книг по title и author (параметры query).
    Доступно всем.
    """
    query = db.query(Book)
    
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    
    return query.all()


@router.get("/books/available", response_model=List[TypeBook])
def get_available_books(
    db: Session = Depends(get_db)
):
    """
    Список доступных книг (available_copies > 0).
    Доступно всем.
    """
    return db.query(Book).filter(Book.available_copies > 0).all()


@router.get("/books", response_model=List[TypeBook])
def get_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Список всех книг.
    Доступно всем.
    """
    return db.query(Book).offset(skip).limit(limit).all()


@router.get("/books/{book_id}", response_model=TypeBookDetail)
def get_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    """
    Детальная информация о книге (без истории читателей).
    Если книга выдана — показывать только available_copies без имён читателей.
    Доступно всем.
    """
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    

    return TypeBookDetail(
        id=book.id,
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        year=book.year,
        genre=book.genre,
        available_copies=book.available_copies,
        is_available=book.available_copies > 0,
        reader_name=None
    )


@router.post("/books", response_model=TypeBook, status_code=201)
def create_book(
    book_data: BookCreate,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """
    Добавить новую книгу.
    Доступно Librarian и Admin.
    """

    if book_data.isbn and db.query(Book).filter(Book.isbn == book_data.isbn).first():
        raise HTTPException(status_code=400, detail="ISBN already exists")
    
    new_book = Book(**book_data.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@router.put("/books/{book_id}", response_model=TypeBook)
def update_book(
    book_id: int,
    book_data: BookCreate,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """
    Обновить информацию о книге.
    Доступно Librarian и Admin.
    """
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book_data.isbn and book_data.isbn != book.isbn:
        existing = db.query(Book).filter(Book.isbn == book_data.isbn).first()
        if existing:
            raise HTTPException(status_code=400, detail="ISBN already exists")
    
    for key, value in book_data.dict(exclude_unset=True).items():
        setattr(book, key, value)
    
    db.commit()
    db.refresh(book)
    return book


@router.delete("/books/{book_id}")
def delete_book(
    book_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Удалить книгу.
    Доступно только Admin.
    """
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully"}
