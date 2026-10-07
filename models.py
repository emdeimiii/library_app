from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
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

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    isbn = Column(String(20), unique=True, nullable=True)
    year = Column(Integer, nullable=True)
    genre = Column(String(50), nullable=True)
    available_copies = Column(Integer, default=0, nullable=False)

    reader_books = relationship("Reader_books", back_populates="book")


class Reader(Base):
    __tablename__ = "readers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    registration_date = Column(String, nullable=False)

    reader_books = relationship("Reader_books", back_populates="reader")



class Reader_books(Base):
    __tablename__ = "reader_books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reader_id = Column(Integer, ForeignKey("readers.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    taken_at = Column(String, nullable=False)
    returned_at = Column(String, nullable=True)

    reader = relationship("Reader", back_populates="reader_books")
    book = relationship("Book", back_populates="reader_books")