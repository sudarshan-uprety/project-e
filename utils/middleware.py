import json
import time
import uuid
from typing import Callable

from fastapi import Request, Response

from utils.log import logger, trace_id_var

# List of sensitive fields to redact
SENSITIVE_FIELDS = [
    "password", "confirm_password", "new_password", "current_password",
    "access_token", "refresh_token"
]


def sanitize_payload(payload):
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            return payload

    if isinstance(payload, dict):
        return {k: "******" if k in SENSITIVE_FIELDS else sanitize_payload(v) for k, v in payload.items()}
    elif isinstance(payload, list):
        return [sanitize_payload(item) for item in payload]
    return payload


async def optimized_logging_middleware(request: Request, call_next: Callable) -> Response:
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
    trace_id_var.set(trace_id)

    start_time = time.time()
    client_ip = request.client.host

    # Get and redact the request body
    try:
        request_body = await request.json()
    except json.JSONDecodeError:
        request_body = (await request.body()).decode() or ""

    sanitized_body = sanitize_payload(request_body)

    log_dict = {
        "url": request.url.path,
        "method": request.method,
        "trace_id": trace_id,
        "client_ip": client_ip,
        "request_payload": sanitized_body
    }

    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        status_code = response.status_code

        log_dict.update({
            "process_time": f"{process_time:.4f}",
            "status_code": status_code
        })

        log_message = json.dumps(log_dict)

        if status_code >= 500:
            logger.error(f"Request failed: {log_message}")
        elif status_code >= 400:
            logger.warning(f"Request resulted in client error: {log_message}")
        else:
            logger.info(f"Request completed successfully: {log_message}")

        return response

    except Exception as e:
        # Log the exception and re-raise it to be handled by global exception handlers
        logger.exception("Unhandled exception during request processing", extra=log_dict)
        raise e
