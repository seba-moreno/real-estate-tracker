from fastapi import Depends, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp
import time
from typing import Dict
from core.dependencies.logger import get_request_logger
from core.logging.logger_with_correlation_id import CorrelationLoggerAdapter


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        logger: CorrelationLoggerAdapter = Depends(get_request_logger),
    ) -> None:
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list[float]] = {}
        self.logger = logger

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        client = request.client
        if client is None or not client.host:
            return Response(
                content="Cannot determine client address.",
                status_code=status.HTTP_400_BAD_REQUEST,
                media_type="text/plain",
            )

        client_ip = client.host
        current_time = time.monotonic()

        if client_ip not in self.requests:
            self.requests[client_ip] = []

        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip] if current_time - ts < 60
        ]

        if len(self.requests[client_ip]) >= self.requests_per_minute:
            self.logger.warning("Rate limit exceeded", extra={"client_ip": client_ip})
            return Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": "60"},
            )

        self.requests[client_ip].append(current_time)

        response = await call_next(request)
        return response
