from auth import get_password_hash
from data import BOOKS_DATA, READERS_DATA, ROLE_DATA
from database import Base, engine
from models import *
from sqlalchemy.orm import Session


Base.metadata.create_all(bind=engine)

def clear_data(session: Session):
    session.query(Reader_books).delete()
    session.query(User).delete()
    session.query(Book).delete()
    session.query(Reader).delete()
    session.commit()

def seed_data(session: Session):

    for b in BOOKS_DATA:
        book = Book(
            id=b["id"],
            title=b["title"],
            author=b["author"],
            isbn=b.get("isbn"),
            year=b.get("year"),
            genre=b.get("genre"),
            available_copies=b.get("available_copies", 0),
            description=b.get("description"),
        )
        session.add(book)

    for a in ROLE_DATA:
        role= User(
            id=a['id'],
            username = a['username'],
            email = a['email'],
            password_hash = get_password_hash(a['password_hash']),
            is_admin = a['is_admin'],
            is_librarian = a['is_librarian'],
            is_active = a['is_active'],
            created_at=a['created_at'],
            updated_at=a['updated_at']
        )
        session.add(role)



    for r in READERS_DATA:
        reader = Reader(
            id=str(r["id"]),
            full_name=r["full_name"],
            email=r["email"],
            phone=r.get("phone"),
            registration_date=r["registration_date"],
        )
        session.add(reader)

    session.flush()

    for r in READERS_DATA:
        for h in r["books_history"]:
            rb = Reader_books(
                reader_id=str(r["id"]),
                book_id=str(h["book_id"]),
                taken_at=h["taken_at"],
                returned_at=h.get("returned_at"),
            )
            session.add(rb)

    session.commit()
    print("База данных успешно заполнена.")


