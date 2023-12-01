import asyncio
import atexit

from aiohttp import ClientSession
from yarl import URL

from app.databases.mongo import Database
from app.schemas.mercury_auth import UpdateCookiesSchema


class BaseSession:
    def __init__(self, service_url: URL, user_id: int, db: Database):
        self._cs = ClientSession()
        self.service_url: URL = service_url
        self.request_url: str = f"{self.service_url}/operatorui"
        self.db: Database = db
        self.user_id: int = user_id
        atexit.register(self._shutdown)

    def _shutdown(self):
        asyncio.run(self._cs.close())

    async def fetch(self, url: URL | str, data=None, **kwargs):
        if data is None:
            async with self._cs.get(url=url, **kwargs) as response:
                await response.read()
        else:
            async with self._cs.post(url=url, data=data, **kwargs) as response:
                await response.read()
        return response

    async def save_cookies(self) -> None:
        cookies = self._cs.cookie_jar.filter_cookies(self.service_url)
        await self.db.mercury_auth.update_cookies(
            UpdateCookiesSchema(
                user_id=self.user_id,
                cookies={key: value.value for key, value in cookies.items()}
            )
        )

    async def load_cookies(self) -> None:
        cookies = await self.db.mercury_auth.get_cookies(user_id=self.user_id)
        if cookies:
            self._cs.cookie_jar.update_cookies(cookies.cookies)

    def clear_cookies(self):
        self._cs.cookie_jar.clear()
