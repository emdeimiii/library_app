from sqlalchemy import create_engine, dec

from sqlalchemy.ext.asyncio import sessionmaker, declarative_base


DATABASE_URL = "sqlite:///./library.db"

engine= create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(
    bink =engine,
    expire_on_commit = False
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.close    