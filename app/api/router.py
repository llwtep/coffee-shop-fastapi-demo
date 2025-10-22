from fastapi import APIRouter
from app.api.auth import authRouter
from app.api.users import userRouter

main_router = APIRouter()
main_router.include_router(userRouter)
main_router.include_router(router=authRouter)
