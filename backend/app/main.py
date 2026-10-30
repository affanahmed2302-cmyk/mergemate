from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.reviews import router as reviews_router
from app.core.config import get_settings
from app.core.exceptions import MergeMateError
from app.schemas.common import ErrorResponse, HealthResponse

settings = get_settings()
app = FastAPI(title="MergeMate API", description="Evidence-first AI Pull Request Intelligence — ProofLayer", version="0.1.0")

app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list + ["*"],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.exception_handler(MergeMateError)
async def handle_mm(request: Request, exc: MergeMateError):
    return JSONResponse(status_code=exc.status_code,
                        content=ErrorResponse(code=exc.code, message=exc.message, details=exc.details).model_dump())

@app.exception_handler(Exception)
async def handle_all(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content=ErrorResponse(code="internal_error", message="Unexpected error").model_dump())

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", version="0.1.0", environment=settings.app_env)

app.include_router(reviews_router)

@app.get("/api/v1/demo")
async def demo():
    return {"message": "POST /api/v1/reviews with {\"pr_url\":\"demo\",\"demo\":true} for sample analysis",
            "timestamp": datetime.now(timezone.utc).isoformat()}
