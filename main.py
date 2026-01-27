from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from core.logging.logger import get_logger
from core.middlewares.correlation import CorrelationIdMiddleware
from core.middlewares.rate_limiter import RateLimiterMiddleware

from database import get_db
from api.v1.routes.concept import router as concept_router
from api.v1.routes.contract import router as contract_router
from api.v1.routes.properties_concepts import router as properties_concepts_router
from api.v1.routes.property import router as property_router
from api.v1.routes.transaction import router as transaction_router

app = FastAPI(
  title="Real State Tracker",
  version="1.0.0",
  description="Internal API for Real State Tracker",
)

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
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

@app.get("/")
def root():
  return {"message": "Hello world"}

@app.get("/health", tags=["Monitoring"])
def health():
  return {"status": "ok"}

@app.get("/health/db", tags=["Monitoring"])
def db_healthcheck(db = Depends(get_db)):
  try:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
  except Exception as e:
    logger = get_logger("app")
    logger.exception("Database healthcheck failed")
    return {"status": "error"}

@app.get("/version", tags=["Meta"])
def version():
  return {"version": app.version}