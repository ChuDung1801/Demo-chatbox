# src/app.py
"""
FastAPI application factory.
"""

from __future__ import annotations

import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.routes.chat   import router as chat_router
from src.routes.users  import router as users_router
from src.routes.movies import router as movies_router

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("cinebot")


def create_app() -> FastAPI:
    app = FastAPI(
        title="CineBot API",
        description="Movie recommendation chatbot powered by LangChain 1.3.0 + Claude",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )

    # ── Request logger ────────────────────────────────────────────────────────
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        t0 = time.perf_counter()
        response = await call_next(request)
        ms = (time.perf_counter() - t0) * 1000
        logger.info("%-6s %-40s %s  %.0fms",
                    request.method, request.url.path,
                    response.status_code, ms)
        return response

    # ── Global exception handler ──────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_error_handler(_request: Request, exc: Exception):
        logger.exception("Unhandled error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Lỗi máy chủ nội bộ. Vui lòng thử lại."},
        )

    # ── Health check ──────────────────────────────────────────────────────────
    @app.get("/health", tags=["system"])
    async def health():
        return {"status": "ok"}

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(chat_router)
    app.include_router(users_router)
    app.include_router(movies_router)

    return app
