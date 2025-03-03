from typing import List

from fastapi import APIRouter, Depends, HTTPException

from database import SessionLocal
from jwt_token import get_current_user
from models import Genre
from routes.admin_func import check_admin

genre_router = APIRouter()

@genre_router.post("/genre_register")
async def genre_register(genre_name: str, current_user: str = Depends(get_current_user)) -> dict:
    check_admin(current_user)
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

@genre_router.get("/get_genres")
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

@genre_router.delete("/delete_genre/{genre_name}")
async def delete_genre(genre_name: str, current_user: str = Depends(get_current_user)) -> dict:
    check_admin(current_user)
    session = SessionLocal()
    try:
        genre = session.query(Genre).filter(Genre.genre_name == genre_name).first()
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
