from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import ReturnDocument

from app.schemas.milk_service import DefaultMilkServiceConfigSchema
from app.schemas.user import UserSchema, UserCreateSchema


class UserRepo:
    def __init__(self, database):
        self.database: AsyncIOMotorDatabase = database
        self.collection: AsyncIOMotorCollection = self.database["users"]

    async def get(self, ident: str) -> UserSchema | None:
        db_user = await self.collection.find_one({"_id": ident})
        return UserSchema(**db_user) if db_user else None

    async def get_by_user_id(self, user_id: int) -> UserSchema | None:
        db_user = await self.collection.find_one({"user_id": user_id})
        return UserSchema(**db_user) if db_user else None

    async def update(self, user: UserCreateSchema) -> UserSchema | None:
        db_user = await self.collection.find_one_and_update(
            {"user_id": user.user_id},
            {"$set": user.model_dump()},
            return_document=ReturnDocument.AFTER
        )
        return UserSchema(**db_user) if db_user else None

    async def create(self, user: UserCreateSchema) -> UserSchema:
        # if user.milk_service_config is None:
        #     user.milk_service_config = DefaultMilkServiceConfigSchema()
        created_user = await self.collection.insert_one(user.model_dump())
        db_user = await self.get(ident=created_user.inserted_id)
        logger.info(f"new user ({db_user}) created")
        return db_user

    async def update_or_create(self, user: UserCreateSchema) -> UserSchema:
        db_user = await self.update(user=UserCreateSchema(**user.model_dump()))
        if db_user is None:
            db_user = await self.create(user=user)
        return db_user
