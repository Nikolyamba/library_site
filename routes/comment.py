from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import SessionLocal
from jwt_token import get_current_user
from models import User
from models.comment_model import Comment

comment_router = APIRouter()

class CreateComment(BaseModel):
    current_user: str = Depends(get_current_user)
    target_user_id: Annotated[int, None] = None
    author_id: Annotated[int, None] = None
    genre_id: Annotated[int, None] = None
    book_id: Annotated[int, None] = None
    content: str
@comment_router.post("/add_comment")
async def create_comment(data: CreateComment) -> dict:
    session = SessionLocal()
    try:
        from_user = session.query(User).filter(User.login == data.current_user).first()
        if not from_user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        new_comment = Comment(user_id = from_user.id, target_user_id = data.target_user_id,
                              book_id = data.book_id, author_id = data.author_id,
                              genre_id = data.genre_id, content = data.content)
        session.add(new_comment)
        session.commit()
        session.refresh(new_comment)
        return {"detail": "комментарий успешно отправлен"}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()
@comment_router.patch("/comments/{comment_id}")
async def edit_comment(comment_id: int, content: str, current_user: str = Depends(get_current_user)) -> dict:
    session = SessionLocal()
    try:
        comment = session.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Комментарий не найден")
        current_user_info = session.query(User).filter(User.login == current_user).first()
        if not current_user_info:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        if not content.strip():
            raise HTTPException(status_code=400, detail="Комментарий не может быть пустым")
        if current_user_info.id == comment.user_id:
            comment.content = content
            session.commit()
            return {"detail": "Комментарий обновлён"}
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

@comment_router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int, current_user: str = Depends(get_current_user)) -> dict:
    session = SessionLocal()
    try:
        comment = session.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Комментарий не найден")
        current_user_info = session.query(User).filter(User.login == current_user).first()
        if not current_user_info:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        if current_user_info.id == comment.user_id or current_user_info.is_admin:
            session.delete(comment)
            session.commit()
            return {"detail": f"Комментарий успешно удалён"}
        raise HTTPException(status_code=403, detail="У вас нет прав для удаления этого комментария")
    except Exception as e:
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Произошла ошибка на сервере")
    finally:
        session.close()

