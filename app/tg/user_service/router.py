from aiogram import Router

from app.tg.user_service import mercury_auth

user_router = Router()
user_router.include_router(mercury_auth.router)
