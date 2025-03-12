from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import SessionLocal
from jwt_token import get_current_user
from models import User
from models.achievment_model import Achievment, UserAchievAssociation

a_router = APIRouter() #achievment_router

class AchievmentRegister(BaseModel):
    a_name: str
    target: int
    genre_id: Optional[int] = None

@a_router.post("/create_achievment")
async def make_achievment(data: AchievmentRegister, current_user: str = Depends(get_current_user)) -> dict:
    session = SessionLocal()
    try:
        current_user_info = session.query(User).filter(User.login == current_user).first()
        if not current_user_info.is_admin:
            raise HTTPException(status_code=400, detail="У вас нет доступа к этой функции!")
        new_achievment = Achievment(a_name = data.a_name, target = data.target, genre_id = data.genre)
        session.add(new_achievment)
        session.commit()
        session.refresh(new_achievment)
        return {"detail": "Новое достижение успешно добавлено!"}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

class InfoAboutAchievment(AchievmentRegister):
    peoples: int

@a_router.get("/achievments/{achievment_id}", response_model = InfoAboutAchievment)
async def get_achivment(achievment_id: int):
    session = SessionLocal()
    try:
        current_achievment = session.query(Achievment).filter(Achievment.id == achievment_id).first()
        if not current_achievment:
            raise HTTPException(status_code=404, detail="Достижние не найдено")
        peoples_that_get_achievment = session.query(UserAchievAssociation).filter\
            (UserAchievAssociation.achievment_id == current_achievment.id).count()
        info_about_achievment = InfoAboutAchievment(a_name = current_achievment.a_name, target = current_achievment.target,
                                                    genre_id = current_achievment.genre_id, peoples = peoples_that_get_achievment)
        return info_about_achievment
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@a_router.get("/achievments", response_model=List[AchievmentRegister])
async def get_all_achivments() -> List[AchievmentRegister]:
    session = SessionLocal()
    try:
        info_about_achievment = []
        achievments = session.query(Achievment).all()
        for achievment in achievments:
            info_about_achievment.append(Achievment(a_name = achievment.a_name, target = achievment.target,
                                                    genre_id = achievment.genre_id))
        return achievments
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()


@a_router.delete("/achievments/{achievment_id}")
async def delete_achievment(achievment_id: int, current_user: str = Depends(get_current_user)) -> dict:
    session = SessionLocal()
    try:
        current_user_info = session.query(User).filter(User.login == current_user).first()
        if not current_user_info.is_admin:
            raise HTTPException(status_code=400, detail="У вас нет доступа к этой функции!")
        current_achievment = session.query(Achievment).filter(Achievment.id == achievment_id).first()
        session.delete(current_achievment)
        session.commit()
        return {"detail": "Достижение успешно удалено!"}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

#TODO: Нужно ли сюда жанры затаскивать?
@a_router.patch("/achievments/{achievment_id}")
async def edit_achievment(data: AchievmentRegister, achievment_id: int,
                          current_user: str = Depends(get_current_user)) -> AchievmentRegister:
    session = SessionLocal()
    try:
        current_user_info = session.query(User).filter(User.login == current_user).first()
        if not current_user_info:
            raise HTTPException(status_code=400, detail="Пользователь не найден")
        if not current_user_info.is_admin:
            raise HTTPException(status_code=400, detail="У вас нет доступа к этой функции!")
        current_achievment = session.query(Achievment).filter(Achievment.id == achievment_id).first()
        if not current_achievment:
            raise HTTPException(status_code=400, detail="Достижение не найдено")
        if data.a_name:
            current_achievment.a_name = data.a_name
        if data.target:
            current_achievment.target = data.target
        session.commit()
        session.refresh(current_achievment)
        return current_achievment
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()





