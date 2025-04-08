from typing import List, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Body

from database import SessionLocal
from jwt_token import get_current_user
from models import Genre, Book
from models.genre_model import BookGenreAssociation
from routes.admin_func import check_admin
from routes.book import AfterBookRegister

genre_router = APIRouter()

@genre_router.post("/genre_register")
async def genre_register(genre_name: Optional[str, Body()], current_user: str = Depends(get_current_user)) -> dict:
    await check_admin(current_user)
    session = SessionLocal()
    try:
        old_genre = session.query(Genre).filter(Genre.genre_name == genre_name).first()
        if old_genre:
            raise HTTPException(status_code=400, detail="Такой жанр уже есть!")
        new_genre = Genre(genre_name = genre_name)
        session.add(new_genre)
        session.commit()
        session.refresh(new_genre)
        return {"detail": f"Жанр {new_genre.genre_name} успешно добавлен!"}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@genre_router.get("/genres")
async def get_all_genres() -> List[str]:
    session = SessionLocal()
    try:
        all_genres = session.query(Genre).order_by(Genre.genre_name).all()
        list_all_genres = []
        for genre in all_genres:
            list_all_genres.append(genre.genre_name)
        return list_all_genres
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@genre_router.get("/genres/{genre_id}/books", response_model=List[AfterBookRegister])
async def get_genre_books(genre_id: str) -> List[AfterBookRegister]:
    session = SessionLocal()
    try:
        current_genre = session.query(Genre).filter(Genre.id == genre_id).first()
        if not current_genre:
            raise HTTPException(status_code=400, detail="Такого жанра нет!")
        genre_books_assoc = session.query(BookGenreAssociation).filter(BookGenreAssociation.genre_id == current_genre.id).all()
        book_ids = []
        for books_id in genre_books_assoc:
            book_ids.append(books_id.book_id)
        genre_books = session.query(Book).filter(Book.id.in_(book_ids)).all()
        info_about_book = []
        for book in genre_books:
            info_about_book.append(AfterBookRegister(title = book.title, profile_picture = book.profile_picture))
        return info_about_book
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@genre_router.delete("/genres/{genre_id}")
async def delete_genre(genre_id: str, current_user: str = Depends(get_current_user)) -> dict:
    await check_admin(current_user)
    session = SessionLocal()
    try:
        genre = session.query(Genre).filter(Genre.id == genre_id).first()
        if not genre:
            raise HTTPException(status_code=400, detail="Такого жанра нет!")
        name = genre.genre_name
        session.delete(genre)
        session.commit()
        return {"detail": f"Жанр {name} успешно удалён"}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@genre_router.patch("genres/{genre_id}")
async def edit_genre(genre_id: str, data: Dict[str, str], current_user: str = Depends(get_current_user)) -> dict:
    await check_admin(current_user)
    session = SessionLocal()
    try:
        current_genre = session.query(Genre).filter(Genre.id == genre_id).first()
        if not current_genre:
            raise HTTPException(status_code=404, detail="Жанр не найден")

        if "genre_name" in data:
            new_genre_name = data.get("genre_name")
            current_genre.genre_name = new_genre_name

        session.commit()
        session.refresh(current_genre)
        return {"detail": current_genre}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="На сервере произошла ошибка")
    finally:
        session.close()
