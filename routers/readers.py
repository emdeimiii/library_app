from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from database import get_db
from models import User, Book, Reader, Reader_books
from schemas import TypeReader, TypeReaderProfile, BookHistoryItem, TypeBook
from dependencies.auth_deps import get_librarian_user, get_admin_user

router = APIRouter()


@router.get("/readers", response_model=List[TypeReader])
def get_readers(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """
    Список всех читателей.
    Доступно Librarian и Admin.
    """
    readers = db.query(Reader).offset(skip).limit(limit).all()
    result = []
    for r in readers:
        history = db.query(Reader_books).filter(Reader_books.reader_id == r.id).all()
        books_history = [
            BookHistoryItem(
                book_id=h.book_id,
                taken_at=h.taken_at,
                returned_at=h.returned_at
            )
            for h in history
        ]
        result.append(TypeReader(
            id=r.id,
            full_name=r.full_name,
            email=r.email,
            phone=r.phone,
            registration_date=r.registration_date,
            books_history=books_history
        ))
    return result


@router.get("/readers/{reader_id}", response_model=TypeReaderProfile)
def get_reader(
    reader_id: int,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """
    Доступно Librarian и Admin.
    """
    reader = db.query(Reader).filter(Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")


    history = db.query(Reader_books).filter(Reader_books.reader_id == reader_id).all()
    
    books_history_with_info = []
    active_books = []
    
    for h in history:
        book = db.query(Book).filter(Book.id == h.book_id).first()
        book_info = None
        if book:
            book_info = TypeBook(
                id=book.id,
                title=book.title,
                author=book.author,
                isbn=book.isbn,
                year=book.year,
                genre=book.genre,
                available_copies=book.available_copies
            )
        
        books_history_with_info.append({
            "book_id": h.book_id,
            "taken_at": h.taken_at,
            "returned_at": h.returned_at,
            "book": book_info
        })
        
        if h.returned_at is None and book:
            active_books.append(book_info)

    return TypeReaderProfile(
        id=reader.id,
        full_name=reader.full_name,
        email=reader.email,
        phone=reader.phone,
        registration_date=reader.registration_date,
        books_history=books_history_with_info,
        active_books=active_books
    )


@router.get("/readers/{reader_id}/books", response_model=List[TypeBook])
def get_reader_active_books(
    reader_id: int,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """
    Только текущие выдачи читателя (не возвращенные книги).
    Доступно Librarian и Admin.
    """
    reader = db.query(Reader).filter(Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")


    active_records = db.query(Reader_books).filter(
        Reader_books.reader_id == reader_id,
        Reader_books.returned_at.is_(None)
    ).all()

    active_book_ids = [r.book_id for r in active_records]
    active_books = db.query(Book).filter(Book.id.in_(active_book_ids)).all()

    return active_books


@router.post("/readers", response_model=TypeReader, status_code=201)
def create_reader(
    reader_data: TypeReader,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """
    Добавить нового читателя.
    Доступно Librarian и Admin.
    """

    if db.query(Reader).filter(Reader.email == reader_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_reader = Reader(
        full_name=reader_data.full_name,
        email=reader_data.email,
        phone=reader_data.phone,
        registration_date=reader_data.registration_date
    )
    db.add(new_reader)
    db.commit()
    db.refresh(new_reader)

    return TypeReader(
        id=new_reader.id,
        full_name=new_reader.full_name,
        email=new_reader.email,
        phone=new_reader.phone,
        registration_date=new_reader.registration_date,
        books_history=[]
    )


@router.put("/readers/{reader_id}", response_model=TypeReader)
def update_reader(
    reader_id: int,
    reader_data: TypeReader,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """
    Доступно Librarian и Admin.
    """
    reader = db.query(Reader).filter(Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")

    if reader_data.email != reader.email:
        existing = db.query(Reader).filter(Reader.email == reader_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

    reader.full_name = reader_data.full_name
    reader.email = reader_data.email
    reader.phone = reader_data.phone
    reader.registration_date = reader_data.registration_date

    db.commit()
    db.refresh(reader)


    history = db.query(Reader_books).filter(Reader_books.reader_id == reader_id).all()
    books_history = [
        BookHistoryItem(
            book_id=h.book_id,
            taken_at=h.taken_at,
            returned_at=h.returned_at
        )
        for h in history
    ]

    return TypeReader(
        id=reader.id,
        full_name=reader.full_name,
        email=reader.email,
        phone=reader.phone,
        registration_date=reader.registration_date,
        books_history=books_history
    )


@router.delete("/readers/{reader_id}")
def delete_reader(
    reader_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Удалить читателя.
    Доступно только Admin.
    Проверяет, нет ли у читателя невозвращенных книг.
    """
    reader = db.query(Reader).filter(Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")


    active_records = db.query(Reader_books).filter(
        Reader_books.reader_id == reader_id,
        Reader_books.returned_at.is_(None)
    ).all()

    if active_records:
        active_book_ids = [r.book_id for r in active_records]
        active_books = db.query(Book).filter(Book.id.in_(active_book_ids)).all()
        book_titles = [book.title for book in active_books]
        
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete reader with active books: {', '.join(book_titles)}"
        )

    db.query(Reader_books).filter(Reader_books.reader_id == reader_id).delete()
    db.delete(reader)
    db.commit()
    
    return {"message": "Reader deleted successfully"}


@router.post("/readers/{reader_id}/borrow/{book_id}")
def borrow_book(
    reader_id: int,
    book_id: int,
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

    if book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="No available copies")


    existing = db.query(Reader_books).filter(
        Reader_books.reader_id == reader_id,
        Reader_books.book_id == book_id,
        Reader_books.returned_at.is_(None)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Reader already has this book")

    history_item = Reader_books(
        reader_id=reader_id,
        book_id=book_id,
        taken_at=date.today().isoformat()
    )
    db.add(history_item)
    book.available_copies -= 1
    db.commit()
    
    return {"message": "Book borrowed successfully"}


@router.post("/readers/{reader_id}/return/{book_id}")
def return_book(
    reader_id: int,
    book_id: int,
    current_user: User = Depends(get_librarian_user),
    db: Session = Depends(get_db)
):
    """Возврат книги от читателя."""
    reader = db.query(Reader).filter(Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")

    history_item = db.query(Reader_books).filter(
        Reader_books.reader_id == reader_id,
        Reader_books.book_id == book_id,
        Reader_books.returned_at.is_(None)
    ).first()

    if not history_item:
        raise HTTPException(status_code=400, detail="Book is not borrowed by this reader")

    history_item.returned_at = date.today().isoformat()

    book = db.query(Book).filter(Book.id == book_id).first()
    book.available_copies += 1

    db.commit()
    return {"message": "Book returned successfully"}