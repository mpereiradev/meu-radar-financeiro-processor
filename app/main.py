import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .api.routes import router
from .infra.scheduler import start_scheduler, shutdown_scheduler

# Configure logging to ensure it shows up in stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    shutdown_scheduler()

app = FastAPI(
    title="Meu Radar Financeiro Processor API",
    description="API for collecting and processing financial documents.",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
