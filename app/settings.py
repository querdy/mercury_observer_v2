import pathlib
import re
from datetime import timedelta
from re import Pattern

from pydantic import computed_field, MongoDsn
from pydantic_core import Url
from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL


saved_msg: dict[int, dict[str, int]] = {}
messages_for_delete: list[dict[str, int]] = list()

BASE_DIR: pathlib.PurePath = pathlib.Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    TZ: str = 'Asia/Yekaterinburg'

    '''Mercury'''
    BASE_MERCURY_URL: URL = URL('https://mercury.vetrf.ru/gve')
    TRAILER_NUMBER_REGEX: Pattern = re.compile(r"(?i)^[АВЕКМНОРСТУХ]{2} ?\d{4}(?<!0000) ?\d{2}( ?R ?U ?S ?)?$")
    MILK_VALID_PURPOSE: list[str] = ['переработка', 'промышленная переработка']
    MILK_VALID_EXPIRATION: list[timedelta] = [timedelta(hours=36)]

    '''Telegram'''
    API_TOKEN: str
    MESSAGE_MAX_LENGTH: int = 4096

    '''Mongo'''
    MONGO_HOST: str
    MONGO_PORT: str
    DATABASE_NAME: str

    @computed_field
    def DB_DSN(self) -> MongoDsn:
        return Url(
            f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}"
        )

    model_config = SettingsConfigDict(env_file=f'{BASE_DIR}/.env', env_file_encoding='utf-8')


settings = Settings()
