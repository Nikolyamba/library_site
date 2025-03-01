from datetime import date
from typing import Annotated, List, Optional

import bcrypt
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from database import SessionLocal
from models import User
from jwt_token import create_access_token, get_current_user
from routes.admin_func import check_admin

user_router = APIRouter()

def hashed_password(password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

class Register(BaseModel):
    login: str
    password: str = Field(min_length=8)
    name: Annotated[str, None] = None
    surname: Annotated[str, None] = None
    email: str
    birthday: Annotated[date, None] = None
    sex: Annotated[str, None] = None
    profile_picture: Annotated[str, None] = None
    is_admin: bool = False

@user_router.post("/register")
async def user_register(user: Register):
    session = SessionLocal()
    old_user = session.query(User).filter((User.login == user.login) | (User.email == user.email)).first()
    if old_user:
        raise HTTPException(status_code=400, detail="Такой логин или email уже существует!")
    user.password = hashed_password(user.password)
    new_user = User(login = user.login,
                    password = user.password,
                    name = user.name,
                    surname = user.surname,
                    email = user.email,
                    birthday = user.birthday,
                    sex = user.sex,
                    profile_picture = user.profile_picture,
                    is_admin = user.is_admin)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    access_token = create_access_token(data={"sub": user.login})
    return {"user": user.login, "token": access_token}

class AllUsersInfo(BaseModel):
    login: str
    profile_picture: Optional[str] = None

@user_router.get("/users", response_model=List[AllUsersInfo])
async def get_all_users() -> List[AllUsersInfo]:
    session = SessionLocal()
    users = session.query(User).order_by(User.login).all()
    info = []
    for user in users:
        info.append(AllUsersInfo(login=user.login, profile_picture=user.profile_picture))
    return info

class UserInfo(BaseModel):
    login: str
    name: Optional[str] = None
    surname: Optional[str] = None
    birthday: Optional[date] = None
    sex: Optional[str] = None
    profile_picture: Optional[str] = None

class UserInfoAdmin(BaseModel):
    id: int
    login: str
    password: str
    name: Optional[str] = None
    surname: Optional[str] = None
    email: str
    birthday: Optional[date] = None
    sex: Optional[str] = None
    profile_picture: Optional[str] = None
    is_admin: bool

@user_router.get("/users/{user_login}")
async def get_user(user_login: str, current_user: str = Depends(get_current_user)) -> dict:
    session = SessionLocal()
    find_user = session.query(User).filter(User.login == user_login).first()
    if not find_user:
        raise HTTPException(status_code=400, detail="Пользователя с таким логином не существует!")
    try:
        check_admin(current_user)
        user_info = UserInfoAdmin(
            id=find_user.id,
            login=find_user.login,
            password=find_user.password,
            name=find_user.name,
            surname=find_user.surname,
            email=find_user.email,
            birthday=find_user.birthday,
            sex=find_user.sex,
            profile_picture=find_user.profile_picture,
            is_admin=find_user.is_admin
        )
        return {"detail": user_info}
    except:
        user_info = UserInfo(
            login=find_user.login,
            name=find_user.name,
            surname=find_user.surname,
            birthday=find_user.birthday,
            sex=find_user.sex,
            profile_picture=find_user.profile_picture
        )
        return {"detail": user_info}

@user_router.delete("/users/{user_login}")
async def delete_user(user_login: str, current_user: str = Depends(get_current_user)) -> dict:
    session = SessionLocal()
    find_user = session.query(User).filter(User.login == user_login).first()
    if not find_user:
        raise HTTPException(status_code=400, detail="Пользователя с таким логином не существует")
    if find_user.login == current_user or check_admin(current_user):
        session.delete(find_user)
        session.commit()
        return {"detail": f"Пользователь {find_user.login} успешно удалён!"}
    raise HTTPException(status_code=403, detail="У вас нет прав для удаления данного пользователя!")

class UserUpdate(BaseModel):
    password: str = Field(min_length = 8)
    name: Optional[str] = None
    surname: Optional[str] = None
    birthday: Optional[str] = None
    sex: Optional[str] = None
    profile_picture: Optional[str] = None

@user_router.patch("/users/{user_login}", response_model=UserInfo)
async def edit_user(user_login: str, data: UserUpdate, current_user: str = Depends(get_current_user)):
    session = SessionLocal()
    find_user = session.query(User).filter(User.login == user_login).first()
    if not find_user:
        raise HTTPException(status_code=400, detail="Пользователя с таким логином не существует")
    if find_user.login == current_user or check_admin(current_user):
        if data.password:
            password = data.password
            find_user.password = hashed_password(password)
        if data.name:
            find_user.name = data.name
        if data.surname:
            find_user.surname = data.surname
        if data.birthday:
            find_user.birthday = data.birthday
        if data.sex:
            find_user.sex = data.sex
        if data.profile_picture:
            find_user.profile_picture = data.profile_picture
        session.commit()
        session.refresh(find_user)
        return find_user
    raise HTTPException(status_code=400, detail="У вас нет прав для редактирования пользователя!")


