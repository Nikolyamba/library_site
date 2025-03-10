from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import SessionLocal
from jwt_token import get_current_user
from models import User
from models.achievment_model import Achievment

a_router = APIRouter() #achievment_router

class AchievmentRegister(BaseModel):
    a_name: str
    target: int

@a_router.post("/create_achievment")
async def make_achievment(data: AchievmentRegister, current_user: str = Depends(get_current_user)) -> dict:
    session = SessionLocal()
    try:
        current_user_info = session.query(User).filter(User.login == current_user).first()
        if not current_user_info.is_admin:
            raise HTTPException(status_code=400, detail="У вас нет доступа к этой функции!")
        new_achievment = Achievment(a_name = data.a_name, target = data.target)
        session.add(new_achievment)
        session.commit()
        session.refresh(new_achievment)
        return {"detail": "Новое достижение успешно добавлено!"}
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




