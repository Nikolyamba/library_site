import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json
import os
from database import init_db
from routes.achievment import a_router
from routes.admin_func import admin_router
from routes.author import author_router
from routes.book import book_router
from routes.comment import comment_router
from routes.genre import genre_router
from routes.sys_func import sys_router
from routes.user import user_router

app = FastAPI()
init_db()

app.include_router(user_router)
app.include_router(author_router)
app.include_router(book_router)
app.include_router(admin_router)
app.include_router(genre_router)
app.include_router(sys_router)
app.include_router(comment_router)
app.include_router(a_router)

@app.get("/.well-known/assetlinks.json", response_class=JSONResponse)
async def assetlinks():
    file_path = os.path.join(os.path.dirname(__file__), 'assetlinks.json')
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8001)