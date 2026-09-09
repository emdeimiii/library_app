from datetime import date

from sqlalchemy import Column, Date, DateTime, ForeignKey, create_engine, Integer, String, Boolean, func

from sqlalchemy.orm import declarative_base, relationship

engine = create_engine('sqlite:///library.db')
Base = declarative_base()

class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column (String, nullable=True)
    year = Column(Integer,nullable=True)
    genre = Column(String,nullable=True)
    available_copies = Column(Integer, default=1)

    reader_books = relationship("ReaderBooks", back_populates="book")

class Reader(Base):
    __tablename__ = 'reader'
    id = Column(Integer, autoincrement=True, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    registration_date = Column(Date, default=date.today)

    reader_books = relationship("ReaderBooks", back_populates="reader")

class Reader_books(Base):
    __tablename__ = 'reader_books'
    id = Column(Integer, autoincrement=True, primary_key=True)
    reader_id = Column(Integer, ForeignKey('reader.id'))
    book_id = Column(Integer, ForeignKey('book.id'))
    taken_at = Column(Date, nullable=False, default=date.today)
    returned_at = Column (Date, nullable=True)

    reader = relationship("Reader", back_populates="reader_books")
    book = relationship("Book", back_populates="reader_books")




class User(Base):
    __tablename__ = 'user'
    id  = Column (Integer, autoincrement=True, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String ,nullable=False)

    is_admin = Column(Boolean, default=False)
    is_librarian = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())
    