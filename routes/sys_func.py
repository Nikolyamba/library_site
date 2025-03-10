from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import json
import os
from database import SessionLocal
from jwt_token import get_current_user
from models import User

sys_router = APIRouter()

sys_router.get("/healthcheck")
async def healthcheck() -> dict:
    response = {"success": True}
    return response

sys_router.get("/get_key")
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

# async def check_and_award_achievment(current_user: str = Depends(get_current_user))
    


