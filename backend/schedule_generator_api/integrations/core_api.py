import json
import time
from urllib import error as urllib_error
from urllib import request as urllib_request

import core_api.schemas.schedule as schemas
from schedule_generator_api.core.config import settings
from schedule_generator_api.core.logging import logger
from shared.schedule_callback import build_schedule_callback_signature


def _post_schedule_generation_callback(
    *,
    callback_url: str,
    raw_body: bytes,
    timestamp: str,
    signature: str,
) -> None:
    request = urllib_request.Request(
        callback_url,
        data=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Timestamp": timestamp,
            "X-Signature": signature,
        },
        method="POST",
    )
    with urllib_request.urlopen(
        request,
        timeout=settings.SCHEDULE_CALLBACK_TIMEOUT_SECONDS,
    ) as response:
        status_code = getattr(response, "status", response.getcode())
        if status_code >= 400:
            raise RuntimeError(
                f"schedule callback returned unexpected status {status_code}"
            )


def send_schedule_generation_callback(
    *,
    dispatch_request: schemas.ScheduleGenerationDispatchRequest,
    callback_payload: schemas.ScheduleGenerationCallbackIn,
) -> None:
    raw_body = json.dumps(callback_payload.model_dump(mode="json")).encode("utf-8")
    timestamp = str(int(time.time()))
    signature = build_schedule_callback_signature(
        secret=settings.SCHEDULE_CALLBACK_SECRET,
        timestamp=timestamp,
        raw_body=raw_body,
    )

    last_error = None
    for attempt in range(settings.SCHEDULE_CALLBACK_MAX_RETRIES):
        try:
            _post_schedule_generation_callback(
                callback_url=dispatch_request.callback_url,
                raw_body=raw_body,
                timestamp=timestamp,
                signature=signature,
            )
            return
        except (urllib_error.URLError, urllib_error.HTTPError, TimeoutError, OSError, RuntimeError) as exc:
            last_error = exc
            logger.error(
                "Schedule callback failed for job %s on attempt %s: %s",
                dispatch_request.job_id,
                attempt + 1,
                exc,
            )
            if attempt + 1 < settings.SCHEDULE_CALLBACK_MAX_RETRIES:
                time.sleep(settings.SCHEDULE_CALLBACK_RETRY_DELAY_SECONDS)

    raise RuntimeError("unable to deliver schedule generation callback") from last_error
