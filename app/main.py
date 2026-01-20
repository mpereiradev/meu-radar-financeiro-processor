from contextlib import asynccontextmanager
from fastapi import FastAPI
from .api.routes import router
from .infra.scheduler import start_scheduler, shutdown_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background scheduler on startup
    start_scheduler()
    yield
    # Shutdown the background scheduler on shutdown
    shutdown_scheduler()

app = FastAPI(lifespan=lifespan)

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
