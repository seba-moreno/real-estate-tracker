from fastapi import Request
from core.logging.logger import get_logger

def get_request_logger(request: Request) -> object:
    return get_logger(__name__, request)
