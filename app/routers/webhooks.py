import asyncio
import json

from loguru import logger
from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.dependencies.security import verify_webhook_signature

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/payment")
async def payment_webhook(
        bg_tasks: BackgroundTasks,
        raw_body: bytes = Depends(verify_webhook_signature)
):
    data = json.loads(raw_body)
    bg_tasks.add_task(process_payment_logic, data)
    return {"status": "success"}

async def process_payment_logic(data: dict):
    await asyncio.sleep(2)
    logger.info(f"Payment processed for order {data.get('order_id')}")