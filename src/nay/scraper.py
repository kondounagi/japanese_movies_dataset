import asyncio
import requests


class Scraper:
    def get(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._get(*args, **kwargs))

    async def _get(self, objects=[]):
        loop = asyncio.get_event_loop()

        tasks = []

        for obj in objects:
            task = loop.run_in_executor(None, requests.get, obj.url)
            tasks.append((obj, task))

        for obj, task in tasks:
            response = await task
            obj.set_content(response.text)
