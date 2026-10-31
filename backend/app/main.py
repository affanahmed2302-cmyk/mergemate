from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.reviews import router as reviews_router
from app.core.config import get_settings
from app.core.exceptions import MergeMateError
from app.schemas.common import ErrorResponse, HealthResponse

settings = get_settings()
app = FastAPI(
    title="MergeMate API",
    description="Evidence-first AI Pull Request Intelligence — ProofLayer",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(MergeMateError)
async def handle_mm(request: Request, exc: MergeMateError):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(code=exc.code, message=exc.message, details=exc.details).model_dump(),
    )


@app.exception_handler(Exception)
async def handle_all(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(code="internal_error", message="Unexpected error").model_dump(),
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", version="0.2.0", environment=settings.app_env)


app.include_router(reviews_router)


@app.get("/api/v1/demo")
async def demo_hint():
    return {
        "message": 'POST /api/v1/reviews with {"pr_url":"demo","demo":true} for sample analysis',
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Serve the product website + app (SPA)
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
INDEX = FRONTEND_DIR / "index.html"

if FRONTEND_DIR.is_dir():
    assets = FRONTEND_DIR / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets)), name="assets")


@app.get("/")
async def spa_root():
    if INDEX.is_file():
        return FileResponse(INDEX)
    return JSONResponse({"message": "Frontend not found. Open frontend/index.html or mount correctly."})


@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    """SPA fallback for public + /app routes. API paths are registered above."""
    if full_path.startswith("api/") or full_path in {"health", "docs", "openapi.json", "redoc"}:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    # Prefer exact static file if present
    candidate = FRONTEND_DIR / full_path
    if candidate.is_file():
        return FileResponse(candidate)
    if INDEX.is_file():
        return FileResponse(INDEX)
    return JSONResponse({"detail": "Not found"}, status_code=404)
