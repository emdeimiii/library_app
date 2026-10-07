from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from typing import List

from database import get_db
from models import User, Book, Reader, BookHistory
from schemas import ( TypeReader, TypeReaderProfile)
from auth import get_librarian_user
import json
from datetime import date

router = APIRouter()


@router.get("/readers", response_model=List[TypeReader])
def get_readers(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """Получение списка всех читателей."""
    readers = db.query(Reader).offset(skip).limit(limit).all()
    result = []
    for r in readers:
        reader_dict = {
            "id": r.id,
            "fullName": r.fullName,
            "email": r.email,
            "phone": r.phone,
            "registrationDate": r.registrationDate,
            "booksHistory": json.loads(r.booksHistory) if r.booksHistory else [],
            "activeBooks": json.loads(r.activeBooks) if r.activeBooks else []
        }
        result.append(TypeReader(**reader_dict))
    return result


@router.get("/readers/{reader_id}", response_model=TypeReaderProfile)
def get_reader(
    reader_id: str,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """Получение читателя по ID."""
    reader = db.query(Reader).filter(Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    
    reader_dict = {
        "id": reader.id,
        "fullName": reader.fullName,
        "email": reader.email,
        "phone": reader.phone,
        "registrationDate": reader.registrationDate,
        "booksHistory": json.loads(reader.booksHistory) if reader.booksHistory else [],
        "activeBooks": json.loads(reader.activeBooks) if reader.activeBooks else []
    }
    return TypeReaderProfile(**reader_dict)


@router.post("/readers", response_model=TypeReader, status_code=201)
def create_reader(
    reader_data: TypeReader,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """Создание нового читателя."""
    if db.query(Reader).filter(Reader.id == reader_data.id).first():
        raise HTTPException(status_code=400, detail="Reader ID already exists")
    
    new_reader = Reader(
        id=reader_data.id,
        fullName=reader_data.fullName,
        email=reader_data.email,
        phone=reader_data.phone,
        registrationDate=reader_data.registrationDate.isoformat(),
        booksHistory=json.dumps([h.dict() for h in reader_data.booksHistory], default=str),
        activeBooks=json.dumps(reader_data.activeBooks)
    )
    db.add(new_reader)
    db.commit()
    db.refresh(new_reader)
    return reader_data


@router.post("/readers/{reader_id}/borrow/{book_id}")
def borrow_book(
    reader_id: str,
    book_id: str,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """Выдача книги читателю."""
    reader = db.query(Reader).filter(Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if not book.isAvailable:
        raise HTTPException(status_code=400, detail="Book is not available")
    

    history_item = BookHistory(
        reader_id=reader_id,
        book_id=book_id,
        taken_at=date.today().isoformat()
    )
    db.add(history_item)

    book.isAvailable = False
    

    active_books = json.loads(reader.activeBooks) if reader.activeBooks else []
    active_books.append(book_id)
    reader.activeBooks = json.dumps(active_books)
    

    books_history = json.loads(reader.booksHistory) if reader.booksHistory else []
    books_history.append({
        "bookId": book_id,
        "takenAt": date.today().isoformat(),
        "returnedAt": None
    })
    reader.booksHistory = json.dumps(books_history, default=str)
    
    db.commit()
    return {"message": "Book borrowed successfully"}


@router.post("/readers/{reader_id}/return/{book_id}")
def return_book(
    reader_id: str,
    book_id: str,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """Возврат книги от читателя."""
    reader = db.query(Reader).filter(Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    
    active_books = json.loads(reader.activeBooks) if reader.activeBooks else []
    if book_id not in active_books:
        raise HTTPException(status_code=400, detail="This book is not borrowed by this reader")
    

    history_item = db.query(BookHistory).filter(
        BookHistory.reader_id == reader_id,
        BookHistory.book_id == book_id,
        BookHistory.returned_at == None
    ).first()
    
    if history_item:
        history_item.returned_at = date.today().isoformat()
    

    book = db.query(Book).filter(Book.id == book_id).first()
    book.isAvailable = True
    

    active_books.remove(book_id)
    reader.activeBooks = json.dumps(active_books)
    

    books_history = json.loads(reader.booksHistory) if reader.booksHistory else []
    for item in books_history:
        if item["bookId"] == book_id and item["returnedAt"] is None:
            item["returnedAt"] = date.today().isoformat()
            break
    reader.booksHistory = json.dumps(books_history, default=str)
    
    db.commit()
    return {"message": "Book returned successfully"}