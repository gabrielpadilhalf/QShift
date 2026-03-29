import hashlib
import hmac


def build_schedule_callback_signature(
    *,
    secret: str,
    timestamp: str,
    raw_body: bytes,
) -> str:
    message = f"{timestamp}.".encode("utf-8") + raw_body
    digest = hmac.new(
        secret.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"


def is_schedule_callback_signature_valid(
    *,
    secret: str,
    timestamp: str,
    raw_body: bytes,
    provided_signature: str,
) -> bool:
    expected_signature = build_schedule_callback_signature(
        secret=secret,
        timestamp=timestamp,
        raw_body=raw_body,
    )
    return hmac.compare_digest(expected_signature, provided_signature)
