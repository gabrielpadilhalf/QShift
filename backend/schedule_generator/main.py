from fastapi import FastAPI

import app.schemas.schedule as schemas
from app.core.logging import logger
from app.services.schedule import ScheduleGenerator

app = FastAPI(title="QShift Schedule Generator")


@app.get("/")
def root():
    logger.info("Generator endpoint / accessed")
    return {"message": "QShift schedule generator is running!"}


@app.get("/healthz")
def healthz():
    logger.info("Generator health check OK")
    return {"status": "ok"}


@app.post(
    "/internal/generate-schedule",
    response_model=schemas.SchedulePreviewOut,
)
def generate_schedule(
    dispatch_request: schemas.ScheduleGenerationDispatchRequest,
):
    schedule_generator = ScheduleGenerator.from_payload(
        payload=dispatch_request.payload
    )
    possible = schedule_generator.check_possibility()

    if possible:
        schedule_out = schedule_generator.generate_schedule()
    else:
        schedule_out = None

    return schemas.SchedulePreviewOut(possible=possible, schedule=schedule_out)
