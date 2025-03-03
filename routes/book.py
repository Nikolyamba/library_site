from typing import Annotated, List

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import and_

from database import SessionLocal
from jwt_token import get_current_user
from models import Book
from routes.admin_func import check_admin

book_router = APIRouter()

class BookRegister(BaseModel):
    title: str
    year: Annotated[int, None] = None
    pages: Annotated[int, None] = None
    profile_picture: str
    author_id: int

class AfterBookRegister(BaseModel):
    title: str

@book_router.post("/register_book", response_model=AfterBookRegister)
async def book_register(book: BookRegister, current_user = Depends(get_current_user)):
    check_admin(current_user)
    session = SessionLocal()
    try:
        old_book = session.query(Book).filter(and_(Book.title == book.title,
                                                   Book.author_id == book.author_id)).first()
        if old_book:
            raise HTTPException(status_code=400, detail="Такая книга уже есть!")
        new_book = Book(title = book.title,
                        year = book.year,
                        pages = book.pages,
                        profile_picture = book.profile_picture,
                        author_id = book.author_id)
        session.add(new_book)
        session.commit()
        session.refresh(new_book)
        return book
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@book_router.get("/books", response_model=List[BookRegister])
async def get_all_books():
    session = SessionLocal()
    try:
        books = session.query(Book).order_by(Book.title).all()
        return books
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@book_router.get("/books/{book_title}", response_model=BookRegister)
async def get_book(book_title: str):
    session = SessionLocal()
    try:
        book = session.query(Book).filter(Book.title == book_title).first()
        if not book:
            raise HTTPException(status_code=400, detail="Книги с таким названием нет!")
        return book
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@book_router.delete("/books/{book_title}")
async def delete_book(book_title: str, current_user = Depends(get_current_user)):
    check_admin(current_user)
    session = SessionLocal()
    try:
        book = session.query(Book).filter(Book.title == book_title).first()
        if not book:
            raise HTTPException(status_code=400, detail="Книги с таким названием нет!")
        session.delete(book)
        session.commit()
        return {"detail": f"Книга {book.title} успешно удалена"}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

