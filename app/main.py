# app/main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler

from app.api.v1.router import api_router
from app.config import get_settings
from app.core.exceptions import setup_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestIDMiddleware, limiter
from app.db.session import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    
    await init_db(settings.database_url)
    yield
    await close_db()

def create_application() -> FastAPI:
    setup_logging()
    settings = get_settings()
    app = FastAPI(lifespan=lifespan)
    setup_exception_handlers(app=app)
    app.state.limiter = limiter
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.include_router(api_router, prefix="/api/v1")

    return app

app = create_application()