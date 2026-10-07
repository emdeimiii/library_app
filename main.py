from fastapi import FastAPI
from database import engine, Base
import models 

from auth_routes import router as auth_router
from routers.users import router as users_router
from routers.books import router as books_router
from routers.readers import router as readers_router
from routers.loans import router as loans_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Management API",
    description="API для управления библиотекой с JWT аутентификацией",
    version="1.0.0"
)

@app.get("/")
def root():
    """Корневой эндпоинт для проверки работоспособности API."""
    return {
        "message": "Welcome to Library Management API",
        "docs": "/docs",
        "status": "running"
    }


app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(users_router, prefix="/api/v1", tags=["Users"])
app.include_router(books_router, prefix="/api/v1", tags=["Books"])
app.include_router(readers_router, prefix="/api/v1", tags=["Readers"])
app.include_router(loans_router, prefix="/api/v1", tags=["Loans"])