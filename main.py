from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.middlewares.correlation import CorrelationIdMiddleware

from routes.concept import router as concept_router
from routes.contract import router as contract_router
from routes.properties_concepts import router as properties_concepts_router
from routes.property import router as property_router
from routes.transaction import router as transaction_router

app = FastAPI()

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

app.include_router(concept_router)
app.include_router(contract_router)
app.include_router(properties_concepts_router)
app.include_router(property_router)
app.include_router(transaction_router)

@app.get("/")
def root():
  return {"message": "Hello world"}

@app.get("/health")
def health():
  return {"status": "ok"}