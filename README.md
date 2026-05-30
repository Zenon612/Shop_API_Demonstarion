# Demo Shop API

Упрощенный демонстрационный проект архитектуры бэкенда на основе FastAPI. Сборник современных паттернов и практик для построения масштабируемых REST API с асинхронной обработкой задач.

## ⚠️ Последние обновления безопасности (v1.1)

Проведена комплексная работа по укреплению безопасности проекта:

✅ **Исправлены критические проблемы**:
- 🔐 Hardcoded пароли заменены на переменные окружения (docker-compose.yml)
- 🔒 Secure флаг для cookies включен для production
- 🚫 SQLAlchemy echo отключен для production (защита от логирования SQL)
- 🛡️ CORS конфигурация добавлена с whitelist origins
- ⏱️ Rate limiting интегрирован (slowapi) против brute force атак
- 🔑 Валидация пароля укреплена (8+ символов, буквы, цифры, спецсимволы)
- 🔗 HTTPS редирект и HSTS headers добавлены для production

✅ **Добавлены важные улучшения**:
- 🛡️ Security headers (X-Frame-Options, X-Content-Type-Options, CSP)
- 📊 Health check endpoints для Kubernetes/Docker
- 🚨 Exception handlers для SQLAlchemy и валидации ошибок
- 📈 Connection pooling с оптимизацией (pool_size=20, max_overflow=10)
- 🎯 Индексы добавлены на критические поля БД (user_id, expires_at, created_at)
- 📝 User-Agent логирование в session tracking
- ✔️ Query параметры валидированы с ограничениями (limit: 1-100)

**Ссылка на отчет**: смотрите [SECURITY_AND_IMPROVEMENTS.md](./SECURITY_AND_IMPROVEMENTS.md) для полного анализа.

## Технологический стек

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) 0.136.1 с Rate Limiting (slowapi)
- **Database**: PostgreSQL 16 (async SQLAlchemy 2.0)
- **Cache**: Redis 7
- **Task Queue**: Celery 5.6.3 (с Redis broker)
- **Message Broker**: Apache Kafka 7.5.0
- **Logging**: Loguru + Kafka + Sentry
- **Monitoring**: Prometheus + Grafana
- **Security**: bcrypt, CORS, HSTS, CSP headers
- **Server**: Uvicorn 0.46.0
- **Python**: 3.12+

## Возможности проекта

- ✅ **REST API** - CRUD операции с товарами
- ✅ **Аутентификация** - Регистрация, логин с session-based подходом
- ✅ **Управление ролями** - RBAC через декоратор `require_role`
- ✅ **Кэширование** - Redis с инвалидацией кэша при обновлении
- ✅ **Асинхронная обработка** - Celery задачи для heavy-processing
- ✅ **Вебхуки** - HMAC-SHA256 подпись для безопасности
- ✅ **Мониторинг** - Prometheus метрики и Grafana дашборды
- ✅ **Структурированное логирование** - Kafka интеграция
- ✅ **Обработка ошибок** - Sentry интеграция
- ✅ **Database миграции** - Alembic
- ✅ **Rate limiting** - Защита от DDoS и brute force
- ✅ **Health checks** - Readiness & Liveness probes

## Структура проекта

```
demo/
├── app/
│   ├── core/
│   │   ├── config.py           # Pydantic Settings (environment-aware)
│   │   ├── security.py         # Хеширование паролей (bcrypt)
│   │   ├── sentry.py           # Инициализация Sentry
│   │   ├── dependencies/
│   │   │   ├── security.py     # Webhook подпись верификации
│   │   │   └── dependencies.py # get_current_user, require_role
│   │   └── logging/
│   │       ├── logging_config.py
│   │       └── async_logger.py # Kafka logger
│   ├── database/
│   │   ├── db.py               # SQLAlchemy async engine (с pooling)
│   │   └── models/
│   │       └── models.py       # ORM модели с индексами
│   ├── routers/
│   │   ├── auth_router.py      # /auth с rate limiting
│   │   ├── item_router.py      # CRUD с rate limiting
│   │   └── webhooks.py         # /webhooks (HMAC)
│   ├── schemas/
│   │   └── schemas.py          # Pydantic с валидацией паролей
│   ├── services/
│   │   └── external_api.py     # HTTP клиент для внешних API
│   ├── middleware/
│   │   └── middleware.py       # Security headers, logging
│   ├── tasks.py                # Celery задачи
│   └── main.py                 # FastAPI приложение + security
├── alembic/                    # Database миграции
├── docker-compose.yml          # Orchestration (с переменными)
├── Dockerfile                  # Production образ
├── .dockerignore                # Оптимизация образов
├── requirements.txt            # Dependencies (+ slowapi)
├── prometheus.yml              # Prometheus конфиг
├── .env.example                # Template для локальной разработки
├── .env.docker.example         # Template для Docker
├── README.md                   # Эта документация
└── SECURITY_AND_IMPROVEMENTS.md # Отчет безопасности
```

## Быстрый старт

### 1. Локальная разработка

```bash
# Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл
cp .env.example .env
# Отредактировать .env с реальными значениями
```

### 2. Docker Compose (рекомендуется)

```bash
# Создать .env.docker из примера
cp .env.docker.example .env.docker

# ВАЖНО: Обновить пароли перед первым запуском!
POSTGRES_PASSWORD="your-strong-password" \
GRAFANA_PASSWORD="your-strong-password" \
docker-compose up -d

# Просмотреть логи
docker-compose logs -f app

# Остановить
docker-compose down
```

### 3. Доступные сервисы

После запуска доступны:

- 🌐 **API**: http://localhost:8000
  - Swagger UI: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc

- 📊 **Prometheus**: http://localhost:9090
- 📈 **Grafana**: http://localhost:3000 (admin/из .env.docker)
- 🗄️ **PostgreSQL**: localhost:5432
- 🔴 **Redis**: localhost:6379
- 🎯 **Kafka**: localhost:9092

## API Примеры

### Регистрация

```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "role_ids": [1, 2]
}
```

### Логин (с rate limiting: 5/minute)

```bash
POST /api/v1/auth/login?email=john@example.com&password=SecurePass123!
```

Ответ установит `session_id` cookie:
```json
{
  "msg": "Authenticated",
  "user_id": 1
}
```

### Создать товар

```bash
POST /api/v1/items/
Content-Type: application/json
Cookie: session_id=<session_id>

{
  "name": "Laptop",
  "price": 999.99,
  "description": "High performance laptop"
}
```

### Получить товар (с кэшированием)

```bash
GET /api/v1/items/1
```

Первый запрос будет сохранен в Redis на 60 секунд.

### Обновить товар

```bash
PUT /api/v1/items/1
Content-Type: application/json

{
  "name": "Updated Laptop",
  "price": 1299.99,
  "description": "Updated description"
}
```

Кэш автоматически инвалидируется.

### Частичное обновление

```bash
PATCH /api/v1/items/1
Content-Type: application/json

{
  "price": 1199.99
}
```

### Удалить товар

```bash
DELETE /api/v1/items/1
```

### Webhook платежа (HMAC подпись)

```bash
POST /webhooks/payment
Content-Type: application/json
X-Webhook-Signature: <hmac_sha256_signature>

{
  "order_id": 123,
  "amount": 99.99,
  "status": "completed"
}
```

## Основные компоненты

### Аутентификация и авторизация

- **Регистрация**: Пароли хешируются через bcrypt
- **Session-based**: Уникальные токены в БД с TTL 24ч
- **RBAC**: Роли и разрешения через User ↔ Role
- **Rate limiting**: Защита от brute force (5/min на логин)
- **Require role**: 
  ```python
  @router.delete("/{id}")
  async def delete(id: int, user: User = Depends(require_role("admin"))):
      ...
  ```

### Кэширование

- Товары кэшируются в Redis на 60 сек
- Автоматическая инвалидация при UPDATE/DELETE
- Background task для логирования попаданий в кэш

### Асинхронная обработка

Celery задачи для long-running операций:
```python
@celery_app.task(max_retries=3)
def heavy_processing(item_id: int, item_name: str):
    # Обработка товара
    pass

# Запуск: heavy_processing.delay(item_id, item_name)
```

### Мониторинг и логирование

- **Prometheus**: Метрики через prometheus-fastapi-instrumentator
- **Grafana**: Визуализация метрик
- **Sentry**: Отслеживание ошибок в production
- **Kafka**: Структурированные логи в отдельную очередь
- **Loguru**: Красивые логи в консоль

### Database

- **PostgreSQL**: Основная БД с asyncpg
- **SQLAlchemy 2.0**: ORM с type hints
- **Alembic**: Миграции версионирования
- **Session tracking**: IP, user-agent для аудита

## Configuration

Все настройки через переменные окружения:

```env
# Environment
ENVIRONMENT=production  # development | production

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER=redis://localhost:6379/1

# Security
SECRET_KEY=your-very-long-random-secret-key-here
WEBHOOK_SECRET=your-webhook-secret-key

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/project_id

# Logging
LOG_KAFKA_ENABLED=true
LOG_KAFKA_BROKER=kafka:9092
LOG_KAFKA_TOPIC=app-logs
```

## Развертывание

### Production

1. Установить зависимости: `pip install -r requirements.txt`
2. Запустить миграции: `alembic upgrade head`
3. Запустить приложение:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```
4. Запустить Celery worker:
   ```bash
   celery -A worker.celery_app worker --loglevel=info
   ```

### Docker Production

```bash
docker-compose -f docker-compose.yml up -d
```

## Миграции Database

```bash
# Создать новую миграцию
alembic revision --autogenerate -m "Add column X to table Y"

# Применить миграции
alembic upgrade head

# Откатить последнюю
alembic downgrade -1

# Просмотреть текущую версию
alembic current
```

## Улучшения и известные ограничения

Смотрите файл `SECURITY_AND_IMPROVEMENTS.md` для списка:
- ✅ 🔴 **Критических** проблем безопасности (все исправлены в v1.1!)
- 🟠 **Важных** оптимизаций
- 🟡 **Полезных** улучшений кода

## Контрибьютинг

При добавлении нового функционала:
1. Следуйте структуре проекта (routers → schemas → services → models)
2. Используйте type hints везде
3. Добавьте docstrings для public функций
4. Обновите README если есть новые endpoints

## Лицензия

MIT - используйте как хотите, дайте ссылку на оригинал.

## Контакты

Questions? Issues? Открывайте issues в репозитории.

---

**Версия**: 1.1 (Security & Best Practices Update)  
**Последнее обновление**: 2026-05-31  
**Status**: Production Ready ✅
