from fastapi import APIRouter, Depends, HTTPException

from database import SessionLocal
from jwt_token import get_current_user
from models import User, Achievment, Genre
from models.achievment_model import UserAchievAssociation
from models.book_model import UserBook, Book

useful_router = APIRouter()

useful_router.get("/healthcheck")
async def healthcheck() -> dict:
    response = {"success": True}
    return response

useful_router.get("/get_key")
async def get_key(current_user: str = Depends(get_current_user)) -> dict:
    session = SessionLocal()
    try:
        current_user_info = session.query(User).filter(User.login == current_user).first()
        if not current_user_info.is_admin:
            raise HTTPException(status_code=400, detail="У вас нет доступа к этой функции!")
        key = "9540fe21-d0fb-4298-bffc-368d703e508c"
        return {"key": key}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

async def check_and_award_achievment(user_id: str):
    session = SessionLocal()
    try:
        achievments = session.query(Achievment).all()
        for achievment in achievments:
            if achievment.genre_id is None:
                user_books_count = session.query(UserBook).filter(UserBook.user_id == user_id).count()
            else:
                user_books_count = session.query(UserBook).join(Book.genres).filter(
                    UserBook.user_id == user_id,
                    Genre.id == achievment.genre_id
                ).count()
            if achievment.target == user_books_count:
                existing_achievment = session.query(UserAchievAssociation).filter(
                    UserAchievAssociation.user_id == user_id,
                    UserAchievAssociation.achievment_id == achievment.id
                ).first()
                if existing_achievment is None:
                    user_achiev_assoc = UserAchievAssociation(achievment_id = achievment.id, user_id = user_id)
                    session.add(user_achiev_assoc)
                    session.commit()
                    session.refresh(user_achiev_assoc)
        return {"detail:" f"Пользователю {User.user_id} выдано достижение"}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

async def check_and_remove_achievment(user_id: str):
    session = SessionLocal()
    try:
        achievments = session.query(Achievment).all()
        for achievment in achievments:
            if achievment.genre_id is None:
                user_books_count = session.query(UserBook).filter(UserBook.user_id == user_id).count()
            else:
                user_books_count = session.query(UserBook).join(Book.genres).filter(
                    UserBook.user_id == user_id,
                    Genre.id == achievment.genre_id
                ).count()
            if achievment.target > user_books_count:
                achievment = session.query(UserAchievAssociation).filter(
                    UserAchievAssociation.user_id == user_id,
                    UserAchievAssociation.achievment_id == achievment.id
                ).first()
                if achievment:
                    session.delete(achievment)
                    session.commit()
        return {"detail:" f"достижение было удалено у пользователя {User.user_id}"}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

    


