from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api.routes.audits import router as audits_router
from app.core.logging import configure_logging

app = FastAPI(
    title="Page Pulse",
    description="Production-grade URL audit service",
    version="0.1.0",
)


app.include_router(audits_router)


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>Page Pulse</title>
        </head>

        <body>
            <h1>Page Pulse</h1>
            <p>Production-grade URL audit service built with FastAPI.</p>

            <footer>
                Built for 
                <a href="https://digitalheroesco.com" target="_blank">
                    Digital Heroes Training Task
                </a>
            </footer>
        </body>
    </html>
    """


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "page-pulse",
    }