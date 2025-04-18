from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from sqlalchemy import and_, func

from database import SessionLocal
from jwt_token import get_current_user
from models import Book, User, Author
from models.book_model import UserBook
from models.genre_model import BookGenreAssociation, Genre
from routes.admin_func import check_admin
from routes.useful_funk import check_and_award_achievment

book_router = APIRouter()

class BookRegister(BaseModel):
    title: str
    year: int
    pages: int
    profile_picture: str
    author_id: int
    genres: list[int]

class AfterBookRegister(BaseModel):
    title: str
    profile_picture: str
    country: str

@book_router.post("/register_book", response_model=AfterBookRegister)
async def book_register(book: BookRegister, current_user = Depends(get_current_user)):
    await check_admin(current_user)
    session = SessionLocal()
    try:
        old_book = session.query(Book).filter(and_(Book.title == book.title,
                                                   Book.author_id == book.author_id)).first()
        if old_book:
            raise HTTPException(status_code=400, detail="Такая книга уже есть!")
        author_country = session.query(Author).filter(Author.id == book.author_id).first()
        new_book = Book(title = book.title,
                        year = book.year,
                        pages = book.pages,
                        profile_picture = book.profile_picture,
                        country = author_country.country,
                        author_id = book.author_id,
                        genres = book.genres)
        session.add(new_book)
        session.commit()
        session.refresh(new_book)
        for genre_id in book.genres:
            session.add(BookGenreAssociation(book_id = new_book.id, genre_id = genre_id))
        session.commit()
        return new_book
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@book_router.get("/books/{sort_type}", response_model=List[BookRegister])
async def get_all_books(sort_type: Optional[str] = None):
    session = SessionLocal()
    try:
        query = session.query(Book)
        if sort_type is None or sort_type == "rating":
            books = query.order_by(Book.average_rating).all()
        elif sort_type == "pages":
            books = query.order_by(Book.pages).all()
        elif sort_type == "year":
            books = query.order_by(Book.year).all()
        elif sort_type == "country":
            books = query.order_by(Book.country).all()
        else:
            raise HTTPException(status_code=400, detail="Недопустимый тип сортировки")
        return books
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

class BookInfo(BookRegister):
    readers: int

class BookInfoAverage(BookInfo):
    average_rating: float

@book_router.get("/books/{book_id}", response_model=BookInfoAverage)
async def get_book(book_id: str):
    session = SessionLocal()
    try:
        book = session.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=400, detail="Книги с таким названием нет!")
        readers_count = session.query(UserBook).filter(UserBook.book_id == book.id).count()
        if readers_count > 0:
            average_rating = session.query(func.avg(UserBook.rating)).filter(UserBook.book_id == book.id, UserBook.rating > 0).scalar()
            average_rating = float(f"{average_rating:.2f}")
        else:
            average_rating = 0.00
        book.average_rating = average_rating
        session.commit()
        book_genres_assoc = session.query(BookGenreAssociation).filter(BookGenreAssociation.book_id == book.id).all()
        genre_ids = []
        for ids in book_genres_assoc:
            genre_ids.append(ids.genre_id)
        genre_titles = []
        genres = session.query(Genre).filter(Genre.id.in_(genre_ids)).all()
        for genre in genres:
            genre_titles.append(genre.genre_name)
        book_info = BookInfoAverage(
            title=book.title,
            year=book.year,
            pages=book.pages,
            profile_picture=book.profile_picture,
            author_id=book.author_id,
            genres=genre_titles,
            readers=readers_count,
            average_rating=average_rating
        )
        return book_info
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@book_router.delete("/books/{book_id}")
async def delete_book(book_id: str, current_user = Depends(get_current_user)) -> dict:
    await check_admin(current_user)
    session = SessionLocal()
    try:
        book = session.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=400, detail="Книги с таким названием нет!")
        book_title = book.title
        session.delete(book)
        session.commit()
        return {"detail": f"Книга {book_title} успешно удалена"}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

class BookUpdate(BaseModel):
    title: str
    year: Optional[int] = None
    pages: Optional[int] = None
    profile_picture: str
    author_id: int
    genres: List[int]

@book_router.patch("/books/{book_id}")
async def edit_book(book_id: str, data: BookUpdate, current_user: str = Depends(get_current_user)) -> BookUpdate:
    session = SessionLocal()
    try:
        current_user_info = session.query(User).filter(User.login == current_user).first()
        if current_user_info.is_author or check_admin(current_user_info.login):
            current_book = session.query(Book).filter(Book.id == book_id).first()
            if not current_book:
                raise HTTPException(status_code=400, detail="Книга не найдена")
            if data.title:
                current_book.title = data.title
            if data.year:
                current_book.year = data.year
            if data.pages:
                current_book.pages = data.pages
            if data.profile_picture:
                current_book.profile_picture = data.profile_picture
            if data.author_id:
                current_book.author_id = data.author_id
            if data.genres:
                current_genres = session.query(BookGenreAssociation).filter(BookGenreAssociation.book_id == current_book.id).all()
                for association in current_genres:
                    session.delete(association)
                current_book.genres = data.genres
                for genre_id in data.genres:
                    if session.query(Genre).filter(Genre.id == genre_id).first() is not None:
                        new_book_genre_association = BookGenreAssociation(book_id = current_book.id, genre_id = genre_id)
                        session.add(new_book_genre_association)
            session.commit()
            session.refresh(current_book)
            return current_book
        raise HTTPException(status_code=400, detail="У вас нет прав для редактирования книги!")
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@book_router.post("/books/{book_id}")
async def add_book_to_user(book_id: str, current_user: str = Depends(get_current_user)) -> dict:
    session = SessionLocal()
    try:
        current_book = session.query(Book).filter(Book.id == book_id).first()
        if not current_book:
            raise HTTPException(status_code=404, detail="Книга не найдена")
        current_user_info = session.query(User).filter(User.login == current_user).first()
        if not current_user_info:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        user_book_entry = UserBook(user_id = current_user_info.id, book_id = current_book.id)
        session.add(user_book_entry)
        session.commit()
        await check_and_award_achievment(current_user_info.id)
        return {"success": True, "response": f"{current_book.title} успешно добавлена пользователю "
                                             f"{current_user_info.login}"}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@book_router.put("/books/{book_id}/rate")
async def rate_book(book_id: str, rating: int = Body(le=10, ge=1),
                    current_user: str = Depends(get_current_user)) -> dict:
    session = SessionLocal()
    try:
        current_user_info = session.query(User).filter(User.login == current_user).first()
        if not current_user_info:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        user_book_assoc = session.query(UserBook).filter(UserBook.book_id == book_id,
                                                              UserBook.user_id == current_user_info.id).first()
        if not user_book_assoc:
            raise HTTPException(status_code=400, detail="Пользователь не прочитал такую книгу")
        user_book_assoc.rating = rating
        session.commit()
        return {"detail": "Оценка успешно добавлена!"}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

