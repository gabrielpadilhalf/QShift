from fastapi import FastAPI

from schedule_generator_api.api.routes.generate import router as generate_router
from schedule_generator_api.core.logging import logger

app = FastAPI(title="QShift Schedule Generator")

app.include_router(generate_router)


@app.get("/")
def root():
    logger.info("Generator endpoint / accessed")
    return {"message": "QShift schedule generator is running!"}


@app.get("/healthz")
def healthz():
    logger.info("Generator health check OK")
    return {"status": "ok"}
