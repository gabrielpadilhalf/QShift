from fastapi import FastAPI
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from core_api.core.config import settings
from core_api.core.db import engine
from core_api.api import api_router
from core_api.core.logging import logger

app = FastAPI(title="QShift API")

app.include_router(api_router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    logger.info("Endpoint / accessed")
    return {"message": "QShift backend is running!", "env": settings.ENV}


@app.get("/healthz")
def healthz():
    logger.info("Health check OK")
    return {"status": "ok"}


@app.get("/healthz/db")
def healthz_db():
    try:
        with engine.begin() as conn:
            result = conn.execute(text("SELECT 1"))
            one = result.scalar_one()
        logger.info("Database connection verified successfully")
        return {"database": "ok", "select_1": one}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"database": "error"}
