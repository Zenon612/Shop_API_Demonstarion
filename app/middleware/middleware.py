import asyncio
from fastapi import FastAPI, Request
import time
from app.core.logging.async_logger import async_kafka_logger


def register_middleware(app: FastAPI):
    @app.middleware("http")
    async def timing_and_logging(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        end_time = time.time()
        duration = end_time - start_time

        try:
            asyncio.create_task(
                async_kafka_logger.emit(
                    level="INFO" if response.status_code < 400 else "WARNING",
                    message=f"{request.method} {request.url.path}",
                    context={
                        "status": response.status_code,
                        "duration": round(duration * 1000, 2),
                    },
                )
            )
        except Exception as e:
            from loguru import logger

            logger.error(f"Логгер упал с {e}")
        return response
