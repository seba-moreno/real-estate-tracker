from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.middlewares.correlation import CorrelationIdMiddleware

app = FastAPI()

app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.add_middleware(CorrelationIdMiddleware)

@app.get("/")
def root():
  return {"message": "Hello world"}

@app.get("/health")
def health():
  return {"status": "ok"}