from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional

from database import get_db
from models import User, Book, Reader, BookHistory
from schemas import (
    LoginRequest, Token, PasswordChangeRequest, 
    UserCreate, UserResponse, UserUpdate,
    TypeBook, TypeBookDetail, TypeReader, TypeReaderProfile,
    BookHistoryItem
)
from auth import (
    authenticate_user, create_access_token, get_password_hash, 
    verify_password, get_current_active_user, get_admin_user,
    get_librarian_user, get_user
)
import json
from datetime import date

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


@router.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Получение информации о текущем авторизованном пользователе.
    Требует валидный JWT токен.
    """
    return current_user


@router.put("/users/me/password")
def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Смена пароля текущего пользователя.
    Требует ввод старого и нового пароля.
    """
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}



@router.get("/users", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Получение списка всех пользователей.
    Доступно только администратору.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Создание нового пользователя.
    Доступно только администратору.
    """
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        is_admin=user_data.is_admin,
        is_librarian=user_data.is_librarian,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_librarian_user), 
    db: Session = Depends(get_db)
):
    """
    Получение информации о пользователе по ID.
    Доступно администратору и библиотекарям.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role_data: UserUpdate,  # ✅ Используем Pydantic схему
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Обновление ролей пользователя.
    Доступно только администратору.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    if role_data.is_admin is not None:
        user.is_admin = role_data.is_admin
    
    if role_data.is_librarian is not None:
        user.is_librarian = role_data.is_librarian
    
    if role_data.is_active is not None:
        user.is_active = role_data.is_active
    
    db.commit()
    db.refresh(user)
    
    return {"message": "User role updated successfully"}


@router.patch("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Деактивация пользователя по ID.
    Доступно только администратору.
    Нельзя деактивировать себя или другого админа.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself"
        )
    
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate another admin"
        )
    
    user.is_active = False
    db.commit()
    
    return {"message": "User deactivated successfully"}


@router.patch("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Активация пользователя по ID.
    Доступно только администратору.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    db.commit()
    
    return {"message": "User activated successfully"}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Удаление пользователя по ID.
    Доступно только администратору.
    Нельзя удалить себя или другого админа.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete another admin"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}




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
    
    # Добавляем в активные книги читателя
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