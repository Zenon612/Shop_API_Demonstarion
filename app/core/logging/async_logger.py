from aiokafka import AIOKafkaProducer
import time
import json
from loguru import logger as sync_logger
from app.core.config import settings


class AsyncKafkaLogger:
    def __init__(self, bootstrap_servers: str, topic: str) -> None:
        self.producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        self.topic = topic

    async def start(self):
        await self.producer.start()

    async def stop(self):
        await self.producer.stop()

    async def emit(self, level: str, message: str, context: dict = None) -> None:
        log_entry = {
            "timestamp": int(time.time()),
            "level": level,
            "message": message,
            "context": context or {},
        }
        try:
            await self.producer.send_and_wait(self.topic, value=log_entry)
        except Exception:
            sync_logger.error(f"Логгер кафки упал: {message}")


def get_logger():
    """
    Возвращает асинхроннный логгер если settings.LOG_KAFKA_ENABLED
    или обычный loguru
    :return:
    """
    if settings.LOG_KAFKA_ENABLED:
        logger = AsyncKafkaLogger(
            bootstrap_servers=settings.LOG_KAFKA_BROKER,
            topic=settings.LOG_KAFKA_TOPIC,
        )
        import asyncio

        asyncio.create_task(logger.start())
        return logger
    else:

        class FallbackLogger:
            async def emit(
                self, level: str, message: str, context: dict = None
            ) -> None:
                sync_logger.log(level, f"{message} | {context or {}}")

                async def start(self):
                    pass

                async def stop(self):
                    pass

        return FallbackLogger()


async_kafka_logger = get_logger()
