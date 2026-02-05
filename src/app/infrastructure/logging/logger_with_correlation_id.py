import logging
from typing import Any, MutableMapping

from app.infrastructure.logging.correlation_context import correlation_id_var


class CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "correlation_id"):
            setattr(record, "correlation_id", correlation_id_var.get())
        return True


class CorrelationLoggerAdapter(logging.LoggerAdapter[Any]):
    def __init__(
        self, logger: logging.Logger, extra: MutableMapping[str, Any] | None = None
    ) -> None:
        super().__init__(logger, dict(extra or {}))

    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> tuple[Any, MutableMapping[str, Any]]:
        extra = kwargs.get("extra") or {}
        extra["correlation_id"] = correlation_id_var.get()
        kwargs["extra"] = extra
        return msg, kwargs


def get_logger(name: str) -> CorrelationLoggerAdapter:
    base = logging.getLogger(name)
    return CorrelationLoggerAdapter(base)
