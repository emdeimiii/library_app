BOOKS_DATA = [
    {
        "id": "1",
        "title": "Мастер и Маргарита",
        "author": "Михаил Булгаков",
        "isbn": "978-5-17-090882-0",
        "year": 1967,
        "genre": "Роман",
        "available_copies": 0, 
        "description": "Мистический роман о дьяволе, посетившем Москву в 1930-х годах."
    },
    {
        "id": "2",
        "title": "Война и мир",
        "author": "Лев Толстой",
        "isbn": "978-5-389-07264-0",
        "year": 1869,
        "genre": "Эпопея",
        "available_copies": 3,  
        "description": "Масштабное произведение о русском обществе в эпоху наполеоновских войн."
    },
    {
        "id": "3",
        "title": "Преступление и наказание",
        "author": "Фёдор Достоевский",
        "isbn": "978-5-17-082643-8",
        "year": 1866,
        "genre": "Роман",
        "available_copies": 2, 
        "description": "Психологический роман о студенте Раскольникове и его теории."
    },
    {
        "id": "4",
        "title": "Евгений Онегин",
        "author": "Александр Пушкин",
        "isbn": "978-5-17-083456-2",
        "year": 1833,
        "genre": "Роман в стихах",
        "available_copies": 0,  
        "description": "История о разочарованном дворянине и трагической любви."
    },
    {
        "id": "5",
        "title": "1984",
        "author": "Джордж Оруэлл",
        "isbn": "978-5-17-092345-1",
        "year": 1949,
        "genre": "Антиутопия",
        "available_copies": 5,  
        "description": "Роман о тоталитарном обществе и Большом Брате."
    },
    {
        "id": "6",
        "title": "Маленький принц",
        "author": "Антуан де Сент-Экзюпери",
        "isbn": "978-5-17-081234-9",
        "year": 1943,
        "genre": "Сказка",
        "available_copies": 4, 
        "description": "Философская сказка о дружбе, любви и ответственности."
    },
    {
        "id": "7",
        "title": "Гарри Поттер и философский камень",
        "author": "Джоан Роулинг",
        "isbn": "978-5-17-085678-3",
        "year": 1997,
        "genre": "Фэнтези",
        "available_copies": 1,  
        "description": "Первая книга о приключениях юного волшебника Гарри Поттера."
    }
]

READERS_DATA = [
    {
        "id": 1,
        "full_name": "Иван Петров",
        "email": "ivan@mail.ru",
        "phone": "+7-999-123-45-67",
        "registration_date": "2024-01-15",
        "books_history": [
            {"book_id": 2, "taken_at": "2024-02-01", "returned_at": "2024-03-15"},
            {"book_id": 3, "taken_at": "2024-03-20", "returned_at": "2024-04-10"},
            {"book_id": 5, "taken_at": "2024-05-01", "returned_at": "2024-06-20"},
            {"book_id": 6, "taken_at": "2024-07-10", "returned_at": "2024-08-01"},
            {"book_id": 1, "taken_at": "2024-08-15", "returned_at": None}
        ]
    },
    {
        "id": 2,
        "full_name": "Мария Иванова",
        "email": "maria@mail.ru",
        "phone": "+7-999-234-56-78",
        "registration_date": "2024-02-20",
        "books_history": [
            {"book_id": 4, "taken_at": "2024-03-01", "returned_at": "2024-04-15"},
            {"book_id": 2, "taken_at": "2024-05-10", "returned_at": None}
        ]
    },
    {
        "id": 3,
        "full_name": "Пётр Сидоров",
        "email": "petr@mail.ru",
        "phone": "+7-999-345-67-89",
        "registration_date": "2024-03-10",
        "books_history": [
            {"book_id": 1, "taken_at": "2024-04-01", "returned_at": "2024-05-20"},
            {"book_id": 3, "taken_at": "2024-06-10", "returned_at": "2024-07-25"},
            {"book_id": 5, "taken_at": "2024-08-01", "returned_at": "2024-09-15"}
        ]
    },
    {
        "id": 4,
        "full_name": "Елена Смирнова",
        "email": "elena@mail.ru",
        "phone": "+7-999-456-78-90",
        "registration_date": "2024-04-05",
        "books_history": [
            {"book_id": 6, "taken_at": "2024-05-01", "returned_at": "2024-06-10"},
            {"book_id": 4, "taken_at": "2024-07-01", "returned_at": "2024-08-20"},
            {"book_id": 1, "taken_at": "2024-09-01", "returned_at": None},
            {"book_id": 2, "taken_at": "2024-09-01", "returned_at": None},
            {"book_id": 3, "taken_at": "2024-09-01", "returned_at": None}
        ]
    },
    {
        "id": 5,
        "full_name": "Алексей Новиков",
        "email": "alexey@mail.ru",
        "phone": "+7-999-567-89-01",
        "registration_date": "2024-05-12",
        "books_history": [
            {"book_id": 5, "taken_at": "2024-06-01", "returned_at": "2024-07-15"},
            {"book_id": 4, "taken_at": "2024-08-01", "returned_at": None}
        ]
    }
]



HISTORY_DATA = [

    (1, 2, "2024-02-01", "2024-03-15"),
    (1, 3, "2024-03-20", "2024-04-10"),
    (1, 5, "2024-05-01", "2024-06-20"),
    (1, 6, "2024-07-10", "2024-08-01"),
    (1, 1, "2024-08-15", None),  # активная выдача


    (2, 4, "2024-03-01", "2024-04-15"),
    (2, 5, "2024-06-15", "2024-07-20"),
    (2, 6, "2024-08-01", "2024-09-10"),
    (2, 2, "2024-05-10", None),  # активная выдача

    (3, 1, "2024-04-01", "2024-05-20"),
    (3, 3, "2024-06-10", "2024-07-25"),
    (3, 5, "2024-08-01", "2024-09-15"),

    (4, 6, "2024-05-01", "2024-06-10"),
    (4, 4, "2024-07-01", "2024-08-20"),
    (4, 1, "2024-09-01", None),  # активная выдача
    (4, 2, "2024-09-01", None),  # активная выдача
    (4, 3, "2024-09-01", None),  # активная выдача

    (5, 5, "2024-06-01", "2024-07-15"),
    (5, 1, "2024-08-20", "2024-09-25"),
    (5, 3, "2024-10-01", "2024-11-10"),
    (5, 4, "2024-08-01", None),  # активная выдача
]

ROLE_DATA = [
    {
    'username': "admin",
    'email': "admin@library.ru",
    'password': "admin123",
    'role': "admin"
    }, 
    {
        'username': "librarian1",
            'email': "lib1@library.ru",
            'password': "lib12345",
            'role': "librarian"},
    
            {
                'username': "librarian2",
                'email': "lib2@library.ru",
                'password': "lib67890",
                'role': "librarian"
                }
]