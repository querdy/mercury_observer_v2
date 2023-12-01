from app.databases.repo.mercury_auth import MercuryAuthRepo
from app.databases.repo.milk_service import MilkServiceConfigRepo
from app.databases.repo.user import UserRepo
from app.settings import settings
from motor.motor_asyncio import AsyncIOMotorClient


class Database:
    def __init__(self, url: str):
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(url)
        self.user: UserRepo = UserRepo(database=self.client[settings.DATABASE_NAME])
        self.mercury_auth: MercuryAuthRepo = MercuryAuthRepo(database=self.client[settings.DATABASE_NAME])
        self.milk_service_config: MilkServiceConfigRepo = MilkServiceConfigRepo(database=self.client[settings.DATABASE_NAME])
