from fastapi import Request
from core.logging.logger_with_correlation_id import CorrelationLoggerAdapter, get_logger


def get_request_logger(request: Request) -> CorrelationLoggerAdapter:
    return get_logger(__name__, request)
