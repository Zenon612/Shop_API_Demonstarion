# Contributing

Спасибо за интерес к нашему проекту! Вот как вы можете помочь.

## Установка для разработки

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/yourusername/demo.git
cd demo
```

### 2. Создайте виртуальное окружение

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установите зависимости

```bash
# Базовые зависимости
pip install -r requirements.txt

# Зависимости для разработки (тестирование, линтинг)
pip install -e ".[dev]"

# Или через pyproject.toml
pip install -e .
```

### 4. Создайте .env файл

```bash
cp .env.example .env
# Отредактируйте .env с вашими значениями
```

### 5. Запустите приложение

```bash
uvicorn app.main:app --reload
```

Приложение будет доступно на http://localhost:8000

## Разработка

### Code Style

Используем **black** и **isort** для форматирования кода:

```bash
# Отформатировать все файлы
black app/
isort app/

# Проверить без изменений
black --check app/
isort --check-only app/
```

### Линтинг

Используем **ruff** для проверки кода:

```bash
# Проверить ошибки
ruff check app/

# Попытаться исправить автоматически
ruff check --fix app/
```

### Type Checking

Используем **mypy** для проверки типов:

```bash
mypy app/
```

### Тестирование

```bash
# Запустить все тесты
pytest

# С отчетом о покрытии
pytest --cov=app

# Конкретный тест
pytest tests/test_auth.py::test_register

# С verbose выводом
pytest -v
```

## Git Workflow

### 1. Создайте ветку для вашей функции

```bash
git checkout -b feature/my-awesome-feature
# или
git checkout -b fix/some-bug
```

### 2. Сделайте коммиты

```bash
# Каждый коммит должен быть логичным и самостоятельным
git add .
git commit -m "feat: Add new amazing feature"
```

**Используйте Conventional Commits**:
- `feat:` - новая функция
- `fix:` - исправление ошибки
- `docs:` - изменение документации
- `style:` - форматирование, без изменения логики
- `refactor:` - рефакторинг кода
- `perf:` - улучшение производительности
- `test:` - добавление тестов
- `chore:` - изменение build процесса, зависимостей
- `security:` - исправление проблем безопасности

Примеры:
```bash
git commit -m "feat: Add rate limiting to authentication endpoints"
git commit -m "fix: Fix SQL injection vulnerability in item search"
git commit -m "docs: Update API documentation for new endpoints"
git commit -m "security: Upgrade cryptography library to fix CVE-2024-XXXXX"
```

### 3. Запушьте и создайте Pull Request

```bash
git push origin feature/my-awesome-feature
```

Затем создайте PR в GitHub с описанием:
- **What** - что изменилось
- **Why** - почему это нужно
- **How** - как это работает
- **Testing** - как это тестировать

## Требования к коду

### Безопасность

- ✅ Нет hardcoded секретов (используйте `.env`)
- ✅ Валидируйте все входные данные (Pydantic)
- ✅ Используйте secure флаги для cookies
- ✅ Добавьте rate limiting для чувствительных endpoints
- ✅ Логируйте все попытки доступа

### Качество кода

- ✅ Type hints везде
- ✅ Docstrings для public функций
- ✅ Обработка исключений
- ✅ Тесты для новой функциональности
- ✅ Отсутствие дублирования кода

### Документация

- ✅ Обновите README если добавили новые endpoints
- ✅ Обновите API примеры если изменили сигнатуры
- ✅ Добавьте комментарии для сложной логики

## Структура проекта

Следуйте этой структуре для новых функций:

```
app/
├── routers/
│   └── my_feature_router.py    # Endpoints
├── schemas/
│   └── my_feature_schemas.py   # Pydantic моделиRequest/Response
├── services/
│   └── my_feature_service.py   # Бизнес логика
├── models/
│   └── my_feature_models.py    # Database модели
└── tests/
    └── test_my_feature.py      # Тесты
```

## Database Миграции

При изменении моделей создайте миграцию:

```bash
# Создать автоматическую миграцию
alembic revision --autogenerate -m "Add new_field to users table"

# Отредактировать migration/versions/xxx_add_new_field.py если нужно

# Применить миграцию
alembic upgrade head
```

## Pre-commit Hooks

Рекомендуется установить pre-commit hooks для автоматической проверки:

```bash
pip install pre-commit
pre-commit install
```

Создайте `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black

  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

## Сообщение об ошибках

Если вы нашли баг:

1. Убедитесь что это действительно баг (перечитайте документацию)
2. Проверьте что баг еще не reported в Issues
3. Создайте Issue с:
   - Описанием бага
   - Шагами для воспроизведения
   - Ожидаемым поведением
   - Фактическим поведением
   - Вашей окружением (OS, Python версия, Docker версия и т.д.)

### Шаблон Issue

```markdown
## Description
Краткое описание проблемы

## Reproduction Steps
1. Сделайте это
2. Потом это
3. Проблема появляется

## Expected Behavior
Что должно было произойти

## Actual Behavior
Что произошло на самом деле

## Environment
- OS: macOS 14.1
- Python: 3.12
- Docker: 24.0
- Browser: Chrome 120
```

## Запрос функции

Если у вас есть идея для новой функции:

1. Проверьте что идея еще не обсуждалась в Discussions
2. Создайте Discussion или Issue с:
   - Описанием функции
   - Почему она нужна
   - Примерами использования

### Шаблон Feature Request

```markdown
## Feature Description
Описание функции

## Motivation
Почему эта функция нужна?

## Example Usage
Как пользователь будет это использовать?

## Alternatives
Какие есть альтернативы?
```

## Процесс Review

Когда вы создали PR:

1. **Автоматические проверки** - GitHub Actions запустит:
   - Линтинг (ruff, black, isort)
   - Type checking (mypy)
   - Тесты (pytest)

2. **Code Review** - maintainer проверит:
   - Качество кода
   - Безопасность
   - Тесты
   - Документация

3. **Изменения** - если нужны исправления:
   - Обновите код в вашей ветке
   - Новые коммиты будут автоматически добавлены в PR

4. **Merge** - когда всё OK:
   - PR будет merged в main
   - Ваш код будет в следующем release!

## Лицензия

Отправляя PR, вы согласны что ваш код будет под MIT лицензией.

## Вопросы?

- 💬 Создайте Discussion для вопросов
- 📧 Email: veber612@mail.ru
- 🐛 Найдите баг? Создайте Issue

**Спасибо за контрибьюцию!** 🙏
