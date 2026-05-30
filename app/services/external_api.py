import asyncio
import aiohttp
from loguru import logger
from typing import Any


class ExternalServiceApi:
    def __init__(self, concurrency_limit: int = 10):
        self.concurrency_limit = concurrency_limit
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.base_url = "https://httpbin.org/delay/1"


    async def fetch_one(self, session: aiohttp.ClientSession, url: str) -> Any | None:
        try:
            async with session.get(url, timeout=10) as response:
                return await response.json()
        except asyncio.TimeoutError as e:
            logger.error(f"Таймаут при запросе: {e}")
        except aiohttp.ClientError as e:
            logger.error(f"ошибка клиента {e} при запросе на {url}")
        return None

    async def fetch_one_with_semaphore(self, session: aiohttp.ClientSession, url: str) -> Any | None:
        async with self.semaphore:
            return await self.fetch_one(session, url)

    async def fetch_all(self, urls: list) -> tuple[Any]:
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_one_with_semaphore(session, url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results