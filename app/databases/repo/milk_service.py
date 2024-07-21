from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import ReturnDocument
from pymongo.results import InsertOneResult

from app.schemas.base import PushSchema, PullSchema, ReverseBooleanSchema
from app.schemas.milk_service import MilkConfigSchema


class MilkServiceConfigRepo:
    def __init__(self, database):
        self.database: AsyncIOMotorDatabase = database
        self.collection: AsyncIOMotorCollection = self.database["milk_service_config"]

    async def get_by_user_id(self, user_id: int) -> MilkConfigSchema | None:
        db_config = await self.collection.find_one(
            {'user_id': user_id},
        )
        if db_config:
            return MilkConfigSchema(**db_config)

    async def create(self, data: MilkConfigSchema) -> MilkConfigSchema:
        created_config: InsertOneResult = await self.collection.insert_one(data.model_dump())
        db_config: MilkConfigSchema = MilkConfigSchema(**(await self.collection.find_one(
            {"_id": created_config.inserted_id})))
        return db_config

    async def get_or_create(self, data: MilkConfigSchema) -> MilkConfigSchema:
        db_config: MilkConfigSchema | None = await self.get_by_user_id(data.user_id)
        if db_config is None:
            db_config: MilkConfigSchema = await self.create(data)
        return db_config

    async def update(self, data: MilkConfigSchema) -> MilkConfigSchema:
        db_config = await self.collection.find_one_and_update(
            {"user_id": data.user_id},
            {"$set": {key: value for key, value in data.model_dump().items() if value is not None}},
            return_document=ReturnDocument.AFTER
        )
        return MilkConfigSchema(**db_config)

    async def reverse_boolean_field(self, data: ReverseBooleanSchema):
        db_config = await self.collection.find_one_and_update(
            {"user_id": data.user_id},
            [
                {"$set": {data.field: {"$not": f"${data.field}"}}}
            ],
            return_document=ReturnDocument.AFTER
        )
        return MilkConfigSchema(**db_config)

    async def push(self, field: str, data: PushSchema) -> MilkConfigSchema:
        db_config = await self.collection.find_one_and_update(
            {"user_id": data.user_id},
            {"$push": {field: {"$each": data.items}}},
            return_document=ReturnDocument.AFTER
        )
        return MilkConfigSchema(**db_config)

    async def pull(self, field: str, data: PullSchema) -> MilkConfigSchema:
        db_config = await self.collection.find_one_and_update(
            {"user_id": data.user_id},
            {"$pull": {field:  data.item}},
            return_document=ReturnDocument.AFTER
        )
        return MilkConfigSchema(**db_config)
