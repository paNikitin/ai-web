## запуск

1. Запустите PostgreSQL. (например, 
docker run -d -p 5433:5432 -e POSTGRES_PASSWORD=root -e POSTGRES_DB=ai_web_db -e POSTGRES_USER=postgres postgres:16.9-alpine
https://docs.docker.com/engine/install/
)
2. Создайте `.env` с переменной `DATABASE_URL`.
3. Примените миграции:
```bash
uv run alembic upgrade head
```
4. Запустите API:
```bash
uv run uvicorn app.main:app --reload --port <..порт..>
```
