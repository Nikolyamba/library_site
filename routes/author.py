from typing import Annotated, List, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import and_

from database import SessionLocal
from jwt_token import get_current_user
from models import Author
from routes.admin_func import check_admin

author_router = APIRouter()

class AuthorRegister(BaseModel):
    name: str
    surname: str
    patronymic: Annotated[str, None] = None
    country: Annotated[str, None] = None
    profile_picture: str

class AfterAuthorRegister(BaseModel):
    name: str
    surname: str
    patronymic: Optional[str] = None

@author_router.post("/register_author", response_model=AfterAuthorRegister)
async def author_register(author: AuthorRegister, current_user: str = Depends(get_current_user)):
    check_admin(current_user)
    session = SessionLocal()
    try:
        old_author = session.query(Author).filter(and_(Author.name == author.name,
                                                   Author.surname == author.surname,
                                                   Author.patronymic == author.patronymic)).first()
        if old_author:
            raise HTTPException(status_code=400, detail="Такой автор уже добавлен!")
        new_author = Author(name = author.name,
                            surname = author.surname,
                            patronymic = author.patronymic,
                            country = author.country,
                            profile_picture = author.profile_picture)
        session.add(new_author)
        session.commit()
        session.refresh(new_author)
        return author
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

class GetAllAuthors(BaseModel):
    name: str
    surname: str
    patronymic: Optional[str] = None
    profile_picture: str

@author_router.get("/authors", response_model=List[GetAllAuthors])
async def get_all_authors() -> List[GetAllAuthors]:
    session = SessionLocal()
    try:
        authors = session.query(Author).order_by(Author.surname).all()
        authors_list = []
        for author in authors:
            authors_list.append(GetAllAuthors(name=author.name, surname=author.surname, patronymic=author.patronymic,
                                              profile_picture=author.profile_picture))
        return authors_list
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

class GetAuthor(BaseModel):
    name: str
    surname: str
    patronimyc: Optional[str] = None
    country: Optional[str] = None
    profile_picture: str

    class Config:
        from_attributes = True

@author_router.get("/authors/{author_surname}", response_model=GetAuthor)
async def get_author(author_surname: str):
    session = SessionLocal()
    try:
        author = session.query(Author).filter(Author.surname == author_surname).first()
        if not author:
            raise HTTPException(status_code=400, detail="Автора с такой фамилией не существует!")
        return author
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@author_router.delete("/authors/{author_surname}")
async def delete_author(author_surname: str, current_user: str = Depends(get_current_user)) -> dict:
    check_admin(current_user)
    session = SessionLocal()
    try:
        author = session.query(Author).filter(Author.surname == author_surname).first()
        if not author:
            raise HTTPException(status_code=400, detail="Автора с такой фамилией не существует!")
        if author.patronymic:
            author_name = author_surname + " " + author.name + " " + author.patronymic
        else:
            author_name = author.surname + " " + author.name
        session.delete(author)
        session.commit()
        return {"detail": f"{author_name} успешно удалён из списка авторов!"}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@author_router.patch("/authors/{author_surname}", response_model=GetAuthor)
def edit_author(author_surname: str, data: GetAuthor, current_user: str = Depends(get_current_user)):
    check_admin(current_user)
    session = SessionLocal()
    try:
        author = session.query(Author).filter(Author.surname == author_surname).first()
        if not author:
            raise HTTPException(status_code=400, detail="Автора с такой фамилией не существует!")
        if data.name:
            author.name = data.name
        if data.surname:
            author.surname = data.surname
        if data.patronimyc:
            author.patronimyc = data.patronimyc
        if data.country:
            author.country = data.country
        if data.profile_picture:
            author.profile_picture = data.profile_picture
        session.commit()
        session.refresh()
        return author
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

