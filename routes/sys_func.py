from fastapi import APIRouter

sys_router = APIRouter()

sys_router.get("/healthcheck")
async def healthcheck() -> dict:
    response = {"success": True}
    return response
