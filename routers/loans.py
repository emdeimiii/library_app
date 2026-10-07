from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import User, Book, Reader, Reader_books
from dependencies.auth_deps import get_librarian_user

router = APIRouter()


class LoanResponse:
    loan_id: int
    reader_id: int
    reader_name: str
    book_id: int
    book_title: str
    taken_at: str
    returned_at: str | None


@router.post("/loans")
def create_loan(
    reader_id: int,
    book_id: int,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):

    reader = db.query(Reader).filter(Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    

    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="Book is not available")
    

    existing = db.query(Reader_books).filter(
        Reader_books.reader_id == reader_id,
        Reader_books.book_id == book_id,
        Reader_books.returned_at.is_(None)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Reader already has this book")
    

    loan = Reader_books(
        reader_id=reader_id,
        book_id=book_id,
        taken_at=datetime.now().isoformat(),
        returned_at=None
    )
    db.add(loan)

    book.available_copies -= 1
    
    db.commit()
    db.refresh(loan)
    
    return {
        "loan_id": loan.id,
        "reader_id": reader_id,
        "reader_name": reader.full_name,
        "book_id": book_id,
        "book_title": book.title,
        "taken_at": loan.taken_at,
        "returned_at": loan.returned_at,
        "message": "Book issued successfully"
    }


@router.post("/loans/{loan_id}/return")
def return_loan(
    loan_id: int,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):

    loan = db.query(Reader_books).filter(
        Reader_books.id == loan_id,
        Reader_books.returned_at.is_(None)
    ).first()
    
    if not loan:
        raise HTTPException(status_code=404, detail="Active loan not found")
    
    loan.returned_at = datetime.now().isoformat()
    
    book = db.query(Book).filter(Book.id == loan.book_id).first()
    book.available_copies += 1
    
    db.commit()
    
    return {
        "loan_id": loan.id,
        "reader_id": loan.reader_id,
        "book_id": loan.book_id,
        "taken_at": loan.taken_at,
        "returned_at": loan.returned_at,
        "message": "Book returned successfully"
    }


@router.get("/loans")
def get_all_loans(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    loans = db.query(Reader_books).offset(skip).limit(limit).all()
    
    result = []
    for loan in loans:
        reader = db.query(Reader).filter(Reader.id == loan.reader_id).first()
        book = db.query(Book).filter(Book.id == loan.book_id).first()
        
        result.append({
            "loan_id": loan.id,
            "reader_id": loan.reader_id,
            "reader_name": reader.full_name if reader else "Unknown",
            "book_id": loan.book_id,
            "book_title": book.title if book else "Unknown",
            "taken_at": loan.taken_at,
            "returned_at": loan.returned_at
        })
    
    return result


@router.get("/loans/active")
def get_active_loans(
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """
    Доступно Librarian и Admin.
    """
    active_loans = db.query(Reader_books).filter(
        Reader_books.returned_at.is_(None)
    ).all()
    
    result = []
    for loan in active_loans:
        reader = db.query(Reader).filter(Reader.id == loan.reader_id).first()
        book = db.query(Book).filter(Book.id == loan.book_id).first()
        
        result.append({
            "loan_id": loan.id,
            "reader_id": loan.reader_id,
            "reader_name": reader.full_name if reader else "Unknown",
            "book_id": loan.book_id,
            "book_title": book.title if book else "Unknown",
            "taken_at": loan.taken_at,
            "returned_at": loan.returned_at
        })
    
    return result