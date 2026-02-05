from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.infrastructure.logging.logger_with_correlation_id import get_logger
from app.infrastructure.logging.logging_config import setup_logging
from app.infrastructure.middlewares.correlation import CorrelationIdMiddleware
from app.infrastructure.middlewares.rate_limiter import RateLimiterMiddleware

from app.core.exceptions.domain_exceptions import NotFoundError, PersistenceError
from app.infrastructure.containers.root_container import RootContainer
from app.infrastructure.persistence.sql_alchemy.database import get_db

from app.presentation.api.v1.routes.concept import router as concept_router
from app.presentation.api.v1.routes.contract import router as contract_router
from app.presentation.api.v1.routes.properties_concepts import (
    router as properties_concepts_router,
)
from app.presentation.api.v1.routes.property import router as property_router
from app.presentation.api.v1.routes.transaction import router as transaction_router


setup_logging()
container = RootContainer()

app = FastAPI(
    title="Real Estate Tracker",
    version="1.0.0",
)
app.container = container  # type: ignore[attr-defined]

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimiterMiddleware, requests_per_minute=100)


API_V1_PREFIX = "/api/v1"
routers_v1 = [
    concept_router,
    contract_router,
    properties_concepts_router,
    property_router,
    transaction_router,
]

for r in routers_v1:
    app.include_router(r, prefix=API_V1_PREFIX)


@app.exception_handler(NotFoundError)
def not_found_handler(_, exc) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(PersistenceError)
def persistence_handler(_, exc) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal database error"},
    )


@app.get("/health", tags=["Monitoring"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/db", tags=["Monitoring"])
def db_healthcheck(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception:
        logger = get_logger("app")
        logger.exception("Database healthcheck failed")
        return {"status": "error"}


@app.get("/version", tags=["Meta"])
def version() -> dict[str, str]:
    return {"version": app.version}
