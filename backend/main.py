import os
import sys
from typing import Any, cast
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
# Allow running as `python backend/main.py` from project root
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from database.connection import init_db_tables
from routes import complaints, chat
from routes.auth_routes import router as auth_router
from limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure all DB tables (users, complaints, etc.) exist
    await init_db_tables()
    yield

from fastapi.responses import JSONResponse

app = FastAPI(
    title="Pharma QMS Complaint API",
    description="Secure Backend API for Customer Complaint Management System",
    version="1.0.0",
    lifespan=lifespan,
)
app.state.limiter = limiter

async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests (Rate limit exceeded: 5 attempts per minute). Please wait 60 seconds before trying again.",
            "error": "Rate limit exceeded"
        }
    )

app.add_exception_handler(RateLimitExceeded, cast(Any, custom_rate_limit_handler))
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Configure CORS Security with Cookie Support (Credentials require explicit origins)
# Production origins from env var CORS_ORIGINS (comma-separated), plus local dev defaults
_default_origins = [
    "https://health-care-five-rosy.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]
_env_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
_all_origins = list(dict.fromkeys(_env_origins + _default_origins))  # deduplicate, env first

app.add_middleware(
    CORSMiddleware,
    allow_origins=_all_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(complaints.router)
app.include_router(chat.router)
app.include_router(auth_router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "Pharma QMS Complaint System"}

if __name__ == "__main__":
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
