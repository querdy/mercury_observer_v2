from bson import ObjectId
from pydantic import BaseModel

from app.schemas.mercury_auth import MercuryAuthSchema


class UserCreateSchema(BaseModel):
    user_id: int
    username: str
    fullname: str


class UserSchema(BaseModel):
    _id: ObjectId
    user_id: int
    username: str
    fullname: str
    mercury_auth_data: MercuryAuthSchema | None = None
    mercury_cookies: dict[str, str] | None = None
