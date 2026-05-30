from contextlib import asynccontextmanager
import redis.asyncio as aioredis
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.hsts import HSTSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.database.models.models import Base
from app.middleware.middleware import register_middleware
from app.core.logging.logging_config import setup_logging
from app.routers.item_router import router as item_router
from app.routers.auth_router import auth_router as auth_router
from app.database.db import engine
from app.core.sentry import init_sentry

init_sentry()
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск приложения")
    app.state.redis = aioredis.from_url(settings.redis_url, decode_responses=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    logger.info("Остановка приложения")
    await app.state.redis.aclose()
    await engine.dispose()


# Инициализация rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(lifespan=lifespan, title="Demo")
app.state.limiter = limiter

# Rate limit exception handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security middleware - HTTPS redirect в production
if settings.is_production:
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(
        HSTSMiddleware,
        max_age=31536000,  # 1 год
        include_subdomains=True,
        preload=True,
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if settings.is_production:
        response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Exception handlers для безопасности
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.error(f"Integrity error: {exc}")
    return JSONResponse(
        status_code=409,
        content={"detail": "Данные уже существуют или нарушено уникальное ограничение"}
    )

@app.exception_handler(SQLAlchemyError)
async def db_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Ошибка базы данных"}
    )

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()}
    )

# Prometheus metrics
instrumentor = Instrumentator()
instrumentor.instrument(app).expose(app, endpoint="/metrics")

# Custom middleware для логирования и timing
register_middleware(app)

# Routes
app.include_router(item_router, prefix="/api/v1", tags=["items"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])

# Health check endpoints
@app.get("/health/live")
async def liveness():
    """Liveness probe для Kubernetes/Docker"""
    return {"status": "ok"}

@app.get("/health/ready")
async def readiness(request: Request):
    """Readiness probe - проверка зависимостей"""
    try:
        # Проверить Redis
        redis = request.app.state.redis
        await redis.ping()
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "error": str(e)}
        )
