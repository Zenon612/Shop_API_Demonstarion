import json
from typing import List
import redis.asyncio as aioredis
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    BackgroundTasks,
    Request,
    Response,
    Query,
)
from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.dependencies.dependencies import get_current_user, require_role
from app.schemas.schemas import ItemCreate, ItemResponse, ItemUpdate, ItemPartialUpdate
from app.tasks import heavy_processing
from app.database.db import get_db
from app.database.models.models import Item, User

router = APIRouter(prefix="/items", tags=["items"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")  # Rate limit для создания товаров
async def create_item(
    request: Request,
    item: ItemCreate,
    db: AsyncSession = Depends(get_db),
):
    new_item = Item(**item.model_dump())
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)

    heavy_processing.delay(new_item.id, new_item.name)
    logger.info(f"Создан товар: {new_item.id}, Celery задача отправлена")
    return new_item


@router.get("/{item_id}", status_code=status.HTTP_200_OK, response_model=ItemResponse)
async def get_item(
    item_id: int,
    request: Request,
    bg_task: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):

    redis_client: aioredis.Redis = request.app.state.redis
    cache_key = f"item:{item_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        bg_task.add_task(log_cache_hit, item_id)
        logger.debug(f"Кэш для {item_id}")
        return json.loads(cached)

    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Позиция не найдена"
        )

    item_pydantic = ItemResponse.model_validate(item)
    item_data = item_pydantic.model_dump()

    await redis_client.setex(cache_key, 60, json.dumps(item_data))
    logger.debug(f"Кэширую {item_id}")
    return item_pydantic


async def log_cache_hit(item_id: int):
    logger.info(f"Логирование доступа к кэшу {item_id}")


@router.get("/", response_model=List[ItemResponse], status_code=status.HTTP_200_OK)
async def get_items(
    response: Response,
    skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
    limit: int = Query(10, ge=1, le=100, description="Максимум элементов на странице"),
    db: AsyncSession = Depends(get_db),
):
    count_result = await db.execute(select(func.count(Item.id)))
    count = count_result.scalar_one_or_none()
    if not count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Объекты не найдены"
        )
    result = await db.execute(select(Item).order_by(Item.id).offset(skip).limit(limit))

    items = result.scalars().all()

    items_data = [ItemResponse.model_validate(item).model_dump() for item in items]
    response.headers["X-Total-Count"] = str(count)
    return items_data


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/minute")  # Rate limit для удаления
async def delete_item(
    request: Request,
    item_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),

):
    query = await db.execute(select(Item).where(Item.id == item_id))
    item = query.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Объект не найден"
        )
    await db.delete(item)
    await db.commit()

    redis_client: aioredis.Redis = request.app.state.redis
    cache_key = f"item:{item_id}"
    await redis_client.delete(cache_key)
    logger.info(f"Объект {item_id} удалён, кэш инвалидирован")
    return None


@router.put(
    "/{item_id}", status_code=status.HTTP_202_ACCEPTED, response_model=ItemResponse
)
@limiter.limit("20/minute")  # Rate limit для обновления
async def update_item(
    request: Request,
    item_id: int,
    item_data: ItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Item).where(Item.id == item_id))

    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Объект не найден"
        )
    item.name = item_data.name
    item.price = item_data.price
    item.description = item_data.description

    await db.commit()
    redis_client: aioredis.Redis = request.app.state.redis
    await redis_client.delete(f"item:{item_id}")
    logger.info(f"Объект{item_id} полностью изменён")
    return item


@router.patch("/{item_id}", status_code=status.HTTP_200_OK, response_model=ItemResponse)
@limiter.limit("20/minute")  # Rate limit для патча
async def patch_item(
    request: Request,
    item_id: int,
    item_data: ItemPartialUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Объект не найден"
        )
    for_update = item_data.model_dump(exclude_unset=True)

    for field, value in for_update.items():
        setattr(item, field, value)

    await db.commit()
    redis_client: aioredis.Redis = request.app.state.redis
    await redis_client.delete(f"item:{item_id}")
    logger.info(f"Объект {item_id} обновил поля: {for_update.keys()}")
    return item
