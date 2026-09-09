from sqlalchemy import create_engine, dec
from fastapi import Depends, HTTPException, Request, status, Depends
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
    except Exception as e:
          db.rollback()
          raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail= f'Нет соединения с базой данных {str(e)}')
    finally:
          db.close()