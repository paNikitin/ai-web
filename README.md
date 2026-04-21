# AI Web Demo

## Что входит в проект

Сервис состоит из трёх пользовательских частей:
- `FastAPI` бэкенд для управления пользователями, API-ключами, chat sessions и историей запросов.
- `Streamlit` интерфейс, который работает только через REST API ьэкенд.
- `Nginx` реверс прокси с единой точкой входа и рейт-лимитинг для chat-эндпоинтов.

Инфраструктурные сервисы:
- `PostgreSQL` для постоянного состояния.
- `Prometheus` для сбора метрик FastAPI.
- `Grafana` с преднастроенным датасорсом и базовым дэшбордом.

## Архитектура

Поток запросов:
`Browser -> Nginx -> Streamlit UI`

API поток:
`Browser/UI -> Nginx(/api/*) -> FastAPI -> PostgreSQL`

Мониторинг:
`Prometheus -> FastAPI /metrics`
`Grafana -> Prometheus`

Сети:
- `frontend_net`: `nginx`, `ui`, `api`
- `backend_net`: `api`, `postgres`
- `monitoring_net`: `api`, `prometheus`, `grafana`

`ui` не имеет доступа к БД. `nginx` не имеет доступа к БД. Постоянные данные БД лежат в `postgres_data`, данные Grafana в `grafana_data`, директория под кэш/веса модели в `model_cache`.


## Запуск

1. Создайте `.env` по примеру:

```bash
cp .env.example .env
```

2. Поднимите проект:

```bash
docker compose up --build -d
```

3. Сервисы доступны:
- приложение: [http://localhost](http://localhost:<port>)
- swagger backend через proxy: [http://localhost:<port>/api/docs](http://localhost:<port>/api/docs)
- prometheus: [http://localhost:9090](http://localhost:<port>)
- grafana: [http://localhost:3000](http://localhost:<port>)

## Примеры API запросов

Создание пользователя:

```bash
curl -X POST http://localhost:<port>/api/users \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "demo_user",
    "email": "demo_user@example.com"
  }'
```

Выпуск API key:

```bash
curl -X POST "http://localhost:<port>/api/users/<user_id>/api-keys" \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "primary-key"
  }'
```

Создание chat session:

```bash
curl -X POST "http://localhost:<port>/api/users/<user_id>/sessions" \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: <token>' \
  -d '{
    "title": "Demo session"
  }'
```

Синхронный chat-запрос:

```bash
curl -X POST http://localhost:<port>/api/chat \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: <token>' \
  -d '{
    "session_id": 1,
    "messages": [
      {"role": "system", "message": "You are concise."},
      {"role": "user", "message": "Say hello"}
    ],
    "temperature": 0.7,
    "max_tokens": 32
  }'
```

Стриминговый chat-запрос:

```bash
curl -N -X POST http://localhost:<port>/api/chat/stream \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: <token>' \
  -d '{
    "session_id": 1,
    "messages": [
      {"role": "user", "message": "Stream a short answer"}
    ],
    "temperature": 0.7,
    "max_tokens": 32
  }'
```

## Мониторинг

Grafana поднимается с готовым датасорсом `Prometheus` и дэшбордом `AI Web Overview`. На дэшборде есть:
- RPS
- latency p95
- число 5xx за последние 5 минут
- распределение запросов по эндпоинтам

## Локальная разработка без Docker

Backend:

```bash
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port <port>
```

Streamlit:

```bash
BACKEND_URL=http://localhost:<port> uv run streamlit run streamlit_app/app.py
```
