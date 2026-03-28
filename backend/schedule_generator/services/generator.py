import app.schemas.schedule as schemas
from schedule_generator.core.logging import logger
from schedule_generator.domain.solver import ScheduleGenerator
from schedule_generator.integrations.core_api import send_schedule_generation_callback


def build_schedule_preview(
    dispatch_request: schemas.ScheduleGenerationDispatchRequest,
) -> schemas.SchedulePreviewOut:
    schedule_generator = ScheduleGenerator.from_payload(
        payload=dispatch_request.payload
    )
    possible = schedule_generator.check_possibility()

    if possible:
        schedule_out = schedule_generator.generate_schedule()
    else:
        schedule_out = None

    return schemas.SchedulePreviewOut(possible=possible, schedule=schedule_out)


def process_schedule_generation_job(
    dispatch_request: schemas.ScheduleGenerationDispatchRequest,
) -> None:
    try:
        preview = build_schedule_preview(dispatch_request)
        callback_payload = schemas.ScheduleGenerationCallbackIn(
            job_id=dispatch_request.job_id,
            status=schemas.ScheduleGenerationJobStatus.DONE,
            result=preview,
            error=None,
        )
    except Exception as exc:
        logger.error("Schedule generation failed for job %s: %s", dispatch_request.job_id, exc)
        callback_payload = schemas.ScheduleGenerationCallbackIn(
            job_id=dispatch_request.job_id,
            status=schemas.ScheduleGenerationJobStatus.FAILED,
            result=None,
            error="schedule generation failed",
        )

    send_schedule_generation_callback(
        dispatch_request=dispatch_request,
        callback_payload=callback_payload,
    )
