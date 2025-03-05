from datetime import date
from typing import Annotated, List, Optional, Union

import bcrypt
from fastapi import APIRouter, HTTPException, Depends, status
import jwt
from pydantic import BaseModel, Field, EmailStr

from database import SessionLocal
from models import User, Book
from jwt_token import create_access_token, get_current_user, create_refresh_token, ALGORITHM, SECRET_KEY
from models.book_model import UserBook
from routes.admin_func import check_admin
from routes.book import BookInfo

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
    email: EmailStr
    birthday: Annotated[date, None] = None
    sex: Annotated[str, None] = None
    profile_picture: Annotated[str, None] = None
    is_admin: bool = False
    is_author: bool = False

@user_router.post("/register")
async def user_register(user: Register) -> dict:
    session = SessionLocal()
    try:
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
                        is_admin = user.is_admin,
                        is_author = user.is_author)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        access_token = create_access_token(data={"sub": user.login})
        refresh_token = create_refresh_token(data={"sub": user.login})
        return {"user": user.login, "access_token": access_token, "refresh_token": refresh_token}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@user_router.post("/token/refresh")
async def refresh_access_token(refresh_token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный refresh токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    session = SessionLocal()
    try:
        user = session.query(User).filter(User.login == login).first()
        if user is None or user.refresh_token != refresh_token:
            raise credentials_exception

        new_access_token = create_access_token(data={"sub": user.login})
        new_refresh_token = create_refresh_token(data={"sub": user.login})
        user.refresh_token = new_refresh_token
        session.commit()

        return {"access_token": new_access_token, "refresh_token": new_refresh_token}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

class AllUsersInfo(BaseModel):
    login: str
    profile_picture: Optional[str] = None

@user_router.get("/users", response_model=List[AllUsersInfo])
async def get_all_users() -> List[AllUsersInfo]:
    session = SessionLocal()
    try:
        users = session.query(User).order_by(User.login).all()
        info = []
        for user in users:
            info.append(AllUsersInfo(login=user.login, profile_picture=user.profile_picture))
        return info
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

class UserInfo(BaseModel):
    login: str
    name: Optional[str] = None
    surname: Optional[str] = None
    birthday: Optional[date] = None
    sex: Optional[str] = None
    profile_picture: Optional[str] = None
    is_author: bool
    readed_books: List[BookInfo]

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
    refresh_token: str
    is_admin: bool
    is_author: bool
    readed_books: List[BookInfo]

@user_router.get("/users/{user_login}")
async def get_user(user_login: str, current_user: str = Depends(get_current_user)) -> Union[UserInfo, UserInfoAdmin]:
    session = SessionLocal()
    try:
        find_user = session.query(User).filter(User.login == user_login).first()
        current_user_info = session.query(User).filter(User.login == current_user).first()
        if not find_user:
            raise HTTPException(status_code=400, detail="Пользователя с таким логином не существует!")
        if current_user_info.is_admin:
            readed_books_info = []
            for read_book in find_user.readed_books:
                readed_books_info.append(read_book.book)
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
                refresh_token=find_user.refresh_token,
                is_admin=find_user.is_admin,
                is_author=find_user.is_author,
                readed_books=readed_books_info
            )
            return user_info
        else:
            readed_books_info = []
            for read_book in find_user.readed_books:
                readed_books_info.append(read_book.book)
            user_info = UserInfo(
                login=find_user.login,
                name=find_user.name,
                surname=find_user.surname,
                birthday=find_user.birthday,
                sex=find_user.sex,
                profile_picture=find_user.profile_picture,
                is_author=find_user.is_author,
                readed_books=readed_books_info
            )
            return user_info
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@user_router.delete("/users/{user_login}")
async def delete_user(user_login: str, current_user: str = Depends(get_current_user)) -> dict:
    session = SessionLocal()
    try:
        find_user = session.query(User).filter(User.login == user_login).first()
        if not find_user:
            raise HTTPException(status_code=400, detail="Пользователя с таким логином не существует")
        if find_user.login == current_user or check_admin(current_user):
            session.delete(find_user)
            session.commit()
            return {"detail": f"Пользователь {find_user.login} успешно удалён!"}
        raise HTTPException(status_code=403, detail="У вас нет прав для удаления данного пользователя!")
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

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
    try:
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
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@user_router.delete("/users/{user_login}/user_books/{book_title}")
async def delete_book_from_user(user_login: str, book_title: str, current_user: str = Depends(get_current_user)) -> dict:
    session = SessionLocal()
    try:
        find_user = session.query(User).filter(User.login == user_login).first()
        if not find_user:
            raise HTTPException(status_code=404, detail="Пользователя с таким логином не существует")
        book = session.query(Book).filter(Book.title == book_title).first()
        if not book:
            raise HTTPException(status_code=404, detail="Такой книги не существует")
        if find_user.login == current_user:
            book_to_delete = session.query(UserBook).filter(UserBook.book_id == book.id,
                                                            UserBook.user_id == find_user.id).first()
            if not book_to_delete:
                raise HTTPException(status_code=404, detail="Книга не найдена у пользователя")
            session.delete(book_to_delete)
            session.commit()
        return {"detail": "Книга успешно удалена у пользователя"}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()






