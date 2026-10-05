from auth import get_password_hash
from data import BOOKS_DATA, READERS_DATA, ROLE_DATA
from database import Base, engine, SessionLocal
from models import User, Book, Reader, Reader_books
from sqlalchemy.orm import Session


def clear_data(session: Session):
    """Очистка всех данных в правильном порядке (сначала зависимые таблицы)."""
    session.query(Reader_books).delete() 
    session.query(Reader).delete()
    session.query(Book).delete()
    session.query(User).delete()   
    session.commit()
    print("🗑️ Данные очищены.")


def seed_data(session: Session):
    """Заполнение БД тестовыми данными."""
    books_map = {}
    readers_map = {}

    for b in BOOKS_DATA:

        existing = None
        if b.get("isbn"):
            existing = session.query(Book).filter(Book.isbn == b["isbn"]).first()
        
        if existing:
            books_map[b["id"]] = existing.id
            print(f"⏭️ Книга уже существует: {b['title']}")
        else:
            book = Book(
                title=b["title"],
                author=b["author"],
                isbn=b.get("isbn"),
                year=b.get("year"),
                genre=b.get("genre"),
                available_copies=b.get("available_copies", 0),
            )
            session.add(book)
            session.flush()
            books_map[b["id"]] = book.id
            print(f"📚 Книга добавлена: {book.title} (id={book.id})")


    users_map = {}
    for a in ROLE_DATA:
        existing = session.query(User).filter(User.username == a["username"]).first()
        
        if existing:
            users_map[a["id"]] = existing.id
            print(f"⏭️ Пользователь уже существует: {a['username']}")
        else:
            user = User(
                username=a["username"],
                email=a["email"],
                password_hash=get_password_hash(a["password"]),
                is_admin=a.get("is_admin", False),
                is_librarian=a.get("is_librarian", False),  # ✅ Было True!
                is_active=a.get("is_active", True),
            )
            session.add(user)
            session.flush()
            users_map[a["id"]] = user.id
            print(f"👤 Пользователь добавлен: {user.username} (admin={user.is_admin}, librarian={user.is_librarian})")


    for r in READERS_DATA:
        existing = session.query(Reader).filter(Reader.email == r["email"]).first()
        
        if existing:
            readers_map[r["id"]] = existing.id
            print(f"⏭️ Читатель уже существует: {r['full_name']}")
        else:
            reader = Reader(
                full_name=r["full_name"],
                email=r["email"],
                phone=r.get("phone"),
                registration_date=r["registration_date"],
            )
            session.add(reader)
            session.flush()
            readers_map[r["id"]] = reader.id
            print(f"📖 Читатель добавлен: {reader.full_name} (id={reader.id})")

    session.flush()


    for r in READERS_DATA:
        real_reader_id = readers_map[r["id"]]
        for h in r["books_history"]:
            real_book_id = books_map[h["book_id"]]
            

            existing_rb = session.query(Reader_books).filter(
                Reader_books.reader_id == real_reader_id,
                Reader_books.book_id == real_book_id,
                Reader_books.taken_at == h["taken_at"]
            ).first()
            
            if existing_rb:
                print(f"⏭️ Запись выдачи уже существует: reader={real_reader_id}, book={real_book_id}")
            else:
                rb = Reader_books(
                    reader_id=real_reader_id,
                    book_id=real_book_id,
                    taken_at=h["taken_at"],
                    returned_at=h.get("returned_at"),
                )
                session.add(rb)

    session.commit()
    print("\n✅ База данных успешно заполнена!")


if __name__ == "__main__":

    print("📦 Создаём таблицы...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы.\n")


    db = SessionLocal()
    try:
        seed_data(db)
    except Exception as e:
        db.rollback()
        print(f"Ошибка: {e}")
    finally:
        db.close()