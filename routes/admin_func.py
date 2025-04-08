from typing import Optional, Union

from fastapi import APIRouter, HTTPException, Depends, Body

from database import SessionLocal
from models import User
from jwt_token import get_current_user

admin_router = APIRouter()

async def check_admin(current_user_login: str) -> Union[bool, dict[str, str]]:
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.login == current_user_login).first()
        if user and user.is_admin:
            return True
        else:
            raise HTTPException(status_code=403, detail="У вас нет прав для выполнения этого действия.")
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@admin_router.post('/add_admin')
async def add_admin(login: Optional[str, Body()], current_user: str = Depends(get_current_user)) -> dict:
    await check_admin(current_user)
    session = SessionLocal()
    try:
        user_to_promote = session.query(User).filter(User.login == login).first()
        if user_to_promote is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден.")
        if user_to_promote.is_admin:
            return {"detail": "Пользователь уже является администратором!"}
        user_to_promote.is_admin = True
        session.commit()
        return {"detail": "Пользователю даны права администратора!"}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@admin_router.post('/add_author')
async def add_author(login: Optional[str, Body()], current_user: str = Depends(get_current_user)) -> dict:
    await check_admin(current_user)
    session = SessionLocal()
    try:
        user_to_promote = session.query(User).filter(User.login == login).first()
        if user_to_promote is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден.")
        if user_to_promote.is_author:
            return {"detail": "Пользователь уже является администратором!"}
        user_to_promote.is_author = True
        session.commit()
        return {"detail": "Пользователю даны права администратора!"}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()
