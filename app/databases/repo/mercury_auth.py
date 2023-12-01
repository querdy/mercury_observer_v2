from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import ReturnDocument

from app.schemas.mercury_auth import UpdateCookiesSchema, CookiesSchema, UpdateLoginAndPasswordSchema, MercuryAuthSchema


class MercuryAuthRepo:
    def __init__(self, database):
        self.database: AsyncIOMotorDatabase = database
        self.collection: AsyncIOMotorCollection = self.database["users"]

    async def update_cookies(self, data: UpdateCookiesSchema) -> None:
        await self.collection.find_one_and_update(
            {"user_id": data.user_id},
            {"$set": {"mercury_cookies": data.cookies}},
            return_document=ReturnDocument.AFTER
        )

    async def get_cookies(self, user_id: int) -> CookiesSchema | None:
        db_user = await self.collection.find_one(
            {"user_id": user_id},
            {"_id": 0, "mercury_cookies": 1}
        )
        cookies = db_user.get('mercury_cookies')
        if cookies:
            return CookiesSchema(cookies=cookies)

    async def update_login_and_password(self, data: UpdateLoginAndPasswordSchema):
        await self.collection.find_one_and_update(
            {"user_id": data.user_id},
            {"$set": {"mercury_auth_data": data.model_dump(exclude={'user_id'})}},
            return_document=ReturnDocument.AFTER
        )

    async def get_login_and_password(self, user_id: str):
        db_user = await self.collection.find_one(
            {"user_id": user_id},
            {"_id": 0, "mercury_auth_data": 1}
        )
        auth_data = db_user.get('mercury_auth_data')
        if auth_data:
            return MercuryAuthSchema(**auth_data)
