from fastapi import FastAPI

from app.api.routes.audits import router as audits_router
from app.core.logging import configure_logging

app = FastAPI(
    title="Page Pulse",
    description="Production-grade URL audit service",
    version="0.1.0",
)


app.include_router(audits_router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "page-pulse",
    }