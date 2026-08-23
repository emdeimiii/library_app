from typing import List

from fastapi import FastAPI, HTTPException

from schemas import TypeBook, TypeBookDetail, TypeReader, TypeReaderProfile

app = FastAPI()

books = [
    {
        "id": "1",
        "title": "Мастер и Маргарита",
        "author": "Михаил Булгаков",
        "year": 1967,
        "genre": "Роман",
        "isAvailable": False,
        "description": "Мистический роман о дьяволе, посетившем Москву в 1930-х годах."
    },
    {
        "id": "2",
        "title": "Война и мир",
        "author": "Лев Толстой",
        "year": 1869,
        "genre": "Эпопея",
        "isAvailable": True,
        "description": "Масштабное произведение о русском обществе в эпоху наполеоновских войн."
    },
    {
        "id": "3",
        "title": "Преступление и наказание",
        "author": "Фёдор Достоевский",
        "year": 1866,
        "genre": "Роман",
        "isAvailable": True,
        "description": "Психологический роман о студенте Раскольникове и его теории."
    }]
readers = [
    {
        "id": "r1",
        "fullName": "Иван Петров",
        "email": "ivan@mail.ru",
        "phone": "+7-999-123-45-67",
        "registrationDate": "2024-01-15",
        "booksHistory": [
            {"bookId": "2", "takenAt": "2024-02-01", "returnedAt": "2024-03-15"},
            {"bookId": "3", "takenAt": "2024-03-20", "returnedAt": "2024-04-10"},
            {"bookId": "5", "takenAt": "2024-05-01", "returnedAt": "2024-06-20"},
            {"bookId": "6", "takenAt": "2024-07-10", "returnedAt": "2024-08-01"},
            {"bookId": "1", "takenAt": "2024-08-15"},
        ],
        "activeBooks": ["1"],
    },
    {
        "id": "r2",
        "fullName": "Мария Иванова",
        "email": "maria@mail.ru",
        "phone": "+7-999-234-56-78",
        "registrationDate": "2024-02-20",
        "booksHistory": [
            {"bookId": "4", "takenAt": "2024-03-01", "returnedAt": "2024-04-15"},
            {"bookId": "2", "takenAt": "2024-05-10"},
        ],
        "activeBooks": ["2"],
    },
    {
        "id": "r3",
        "fullName": "Пётр Сидоров",
        "email": "petr@mail.ru",
        "phone": "+7-999-345-67-89",
        "registrationDate": "2024-03-10",
        "booksHistory": [
            {"bookId": "1", "takenAt": "2024-04-01", "returnedAt": "2024-05-20"},
            {"bookId": "3", "takenAt": "2024-06-10", "returnedAt": "2024-07-25"},
            {"bookId": "5", "takenAt": "2024-08-01", "returnedAt": "2024-09-15"},
        ],
        "activeBooks": [],
    }]
@app.get("/books", response_model=List[TypeBook] )
def get_books():
    return books

@app.get("/readers",response_model=List[TypeReader] )
def get_readers():
    return readers

    
@app.get("/readers/{reader_id}", response_model=TypeReaderProfile)
def get_reader(reader_id: str):
    for reader in readers:
        if reader["id"] == reader_id:
            return reader
    raise HTTPException(status_code=404, detail="Читатель не найден")

@app.get("/books/{books_id}", response_model=TypeBookDetail)
def get_book_info(books_id: str):
    for book in books:
        if book["id"] == books_id:
            return book
    raise HTTPException(status_code=404, detail="Книга не найдена")

