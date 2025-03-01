from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Body

from database import SessionLocal
from models import User
from jwt_token import get_current_user

admin_router = APIRouter()

def check_admin(current_user: str = Depends(get_current_user)) -> None:
    session = SessionLocal()
    user = session.query(User).filter(User.login == current_user).first()
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="У вас нет прав администратора!")

@admin_router.post('/add_admin')
def add_admin(login: Annotated[str, Body()], current_user: str = Depends(get_current_user)) -> dict:
    check_admin(current_user)
    session = SessionLocal()
    user_to_promote = session.query(User).filter(User.login == login).first()
    if user_to_promote is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")
    if user_to_promote.is_admin:
        return {"detail": "Пользователь уже является администратором!"}
    user_to_promote.is_admin = True
    session.commit()
    return {"detail": "Пользователю даны права администратора!"}
