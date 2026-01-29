import logging
from typing import Any, MutableMapping
from fastapi import Request


class CorrelationLoggerAdapter(logging.LoggerAdapter[logging.Logger]):
    def __init__(
        self, logger: logging.Logger, extra: MutableMapping[str, Any] | None = None
    ) -> None:
        super().__init__(logger, dict(extra or {}))

    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> tuple[Any, MutableMapping[str, Any]]:
        extra = kwargs.get("extra")
        if not isinstance(extra, dict):
            extra = dict(extra or {})
        if "correlation_id" not in extra:
            extra["correlation_id"] = "N/A"

        kwargs["extra"] = extra
        return msg, kwargs


def get_logger(name: str, request: None | Request = None) -> CorrelationLoggerAdapter:
    logger = logging.getLogger(name)
    correlation_id = (
        getattr(request.state, "correlation_id", "N/A") if request else "N/A"
    )
    return CorrelationLoggerAdapter(logger, {"correlation_id": correlation_id})
