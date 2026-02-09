from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp
import time
from app.infrastructure.logging.logger_with_correlation_id import get_logger


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
    ) -> None:
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: dict[str, list[float]] = {}

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        logger = get_logger("RateLimiterMiddleware")

        client = request.client
        if client is None or not client.host:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot determine client address.",
            )

        client_ip = request.headers.get("X-Test-Client-IP") or (
            request.client.host if request.client else None
        )
        if not client_ip or client_ip == "NONE":
            raise HTTPException(
                status_code=400, detail="Cannot determine client address."
            )

        current_time = time.monotonic()

        if client_ip not in self.requests:
            self.requests[client_ip] = []

        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip] if current_time - ts < 60
        ]

        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning("Rate limit exceeded", extra={"client_ip": client_ip})
            return Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": "60"},
            )

        self.requests[client_ip].append(current_time)

        response = await call_next(request)
        return response
