from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_librarian = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)



class Book(Base):
    __tablename__ = "books"

    id = Column(String, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    genre = Column(String(50), nullable=False)
    description = Column(String(1000), default="")
    isAvailable = Column(Boolean, default=True, nullable=False)


class Reader(Base):
    __tablename__ = "readers"

    id = Column(String, primary_key=True, index=True)
    fullName = Column(String(200), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    registrationDate = Column(String, nullable=False)

    # Связи
    booksHistory = Column(String, default="[]")
    activeBooks = Column(String, default="[]")


class BookHistory(Base):
    __tablename__ = "book_history"

    id = Column(Integer, primary_key=True, index=True)
    reader_id = Column(String, ForeignKey("readers.id"), nullable=False)
    book_id = Column(String, ForeignKey("books.id"), nullable=False)
    taken_at = Column(String, nullable=False)
    returned_at = Column(String, nullable=True)