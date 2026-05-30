import asyncio

import sentry_sdk
from celery import Celery
from celery.signals import task_failure
from app.services.external_api import ExternalServiceApi
from app.core.config import settings
import time
from loguru import logger

celery_app = Celery("worker", broker=settings.celery_broker, backend=settings.redis_url)

@task_failure.connect
def handle_task_failure(**kw):
    exception = kw.get('exception')
    sentry_sdk.capture_exception(exception)

@celery_app.task(bind=True, max_retries=3)
def heavy_processing(self, item_id: int, item_name: str):
    logger.info(f"[Celery] запускаю процесс обработки товара {item_id}")
    time.sleep(3)
    logger.success(f"Товар {item_id} успешно обработан")
    return {"status": "done", "item_id": item_id, "item_name": item_name}


@celery_app.task(bind=True, max_retries=3)
def sync_with_external(self, item_ids: list[int]):
    logger.info(f"Начинаю синхронизацию {len(item_ids)} товаров")

    urls = [f"https://httpbin.org/delay/1?id={item_id}" for item_id in item_ids]

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        client = ExternalServiceApi(concurrency_limit=5)
        results = loop.run_until_complete(client.fetch_all(urls))

        successful = sum(1 for r in results if not isinstance(r, Exception))
        logger.success(f"Синхронизация завершена. Успешно: {successful}/{len(results)}")
        return results

    except Exception as exc:
        logger.error(f"Ошибка синхронизации: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)
    finally:
        loop.close()