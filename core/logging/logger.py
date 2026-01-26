from typing import Optional
from fastapi import Request
import logging

class CorrelationLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.get("extra") or {}
        if "correlation_id" not in extra:
            extra["correlation_id"] = "N/A"
        kwargs["extra"] = extra
        return msg, kwargs

def get_logger(name: str, request: Optional[Request] = None) -> logging.LoggerAdapter:
    logger = logging.getLogger(name)
    correlation_id = getattr(request.state, "correlation_id", "N/A") if request else "N/A"
    return CorrelationLoggerAdapter(logger, {"correlation_id": correlation_id})
