import json
import logging
import time
from contextlib import asynccontextmanager
from logging.config import dictConfig
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text

from app.config import get_settings
from app.database.database import engine
from app.ml_model.ml_model import MockLLM
from app.routers.router import router

settings = get_settings()

with (Path(__file__).resolve().parent.parent / "log_config.json").open(
    encoding="utf-8"
) as log_config_file:
    dictConfig(json.load(log_config_file))

logger = logging.getLogger(__name__)

ml_model_state: dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    started_at = time.perf_counter()
    async with engine.begin() as connection:
        await connection.execute(text("SELECT 1"))
    ml_model_state["ml_model"] = MockLLM(cache_dir=settings.MODEL_CACHE_DIR)
    logger.info(
        "Server is ready to accept connections in %.1fms.",
        (time.perf_counter() - started_at) * 1000,
    )
    yield
    ml_model_state.clear()
    await engine.dispose()
    logger.info("Application shutdown completed.")


app = FastAPI(title=settings.APP_TITLE, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    excluded_handlers=["/metrics"],
).instrument(app).expose(app, include_in_schema=False)


class ContextLengthExceeded(Exception):
    def __init__(self, limit: int):
        self.limit = limit


@app.exception_handler(ContextLengthExceeded)
async def context_length_handler(request: Request, exc: ContextLengthExceeded):
    logger.warning("LLM context overflow on `%s`.", request.url.path)

    return JSONResponse(
        status_code=400,
        content={"error": f"Input message is greater than {exc.limit} symbols."},
    )


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error on `%s`: %s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=422,
        content={
            "error": "Request validation failed.",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on `%s`.", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error."},
    )


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    started_at = time.perf_counter()
    response = await call_next(request)
    process_time_ms = (time.perf_counter() - started_at) * 1000
    response.headers["X-Process-Time"] = f"{process_time_ms:.1f}ms"
    logger.info(
        "%s %s -> %s in %.1fms",
        request.method,
        request.url.path,
        response.status_code,
        process_time_ms,
    )
    return response
