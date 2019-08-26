import aiohttp
import asyncio
from abc import ABC, abstractmethod

MAX_CONNECTIONS = 20


class Scrapable(ABC):
    @property
    @abstractmethod
    def url():
        pass

    @abstractmethod
    def set_content():
        pass


class Scraper:
    def get(self, objects=[]):
        loop = asyncio.get_event_loop()

        conn = aiohttp.TCPConnector(limit=MAX_CONNECTIONS)
        session = aiohttp.ClientSession(connector=conn, loop=loop)

        tasks = [self._get(obj, session) for obj in objects]

        loop.run_until_complete(asyncio.gather(*tasks))
        loop.run_until_complete(session.close())

    async def _get(self, obj, session):
        async with session.get(obj.url) as response:
            obj.set_content(await response.text())
