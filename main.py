from fastapi import FastAPI
from database import engine, Base
import models 

from auth_routes import router as auth_router
from auth_routes import router as app_router


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


app.include_router(auth_router, prefix="/api/v1", tags=["Authentication & Users"])
app.include_router(app_router, prefix="/api/v1", tags=["Library Management"])