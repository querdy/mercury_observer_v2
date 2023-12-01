from pydantic import BaseModel


class MercuryAuthSchema(BaseModel):
    login: str
    password: str


class UpdateLoginAndPasswordSchema(BaseModel):
    user_id: int
    login: str
    password: str


class UpdateCookiesSchema(BaseModel):
    user_id: int
    cookies: dict[str, str]


class CookiesSchema(BaseModel):
    cookies: dict[str, str]
