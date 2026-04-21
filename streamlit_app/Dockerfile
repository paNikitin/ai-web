FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy
ENV BACKEND_URL=http://api:8001

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY streamlit_app ./streamlit_app

RUN uv sync --frozen --no-install-project

CMD ["sh", "-c", "uv run streamlit run streamlit_app/app.py --server.address=0.0.0.0 --server.port=8501 --server.headless=true"]
