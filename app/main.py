# app/main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.config import get_settings
from app.core.exceptions import setup_exception_handlers
from app.db.session import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    
    await init_db(settings.database_url)
    yield
    await close_db()

def create_application() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    setup_exception_handlers(app=app)
    app.include_router(api_router, prefix="/api/v1")

    return app

app = create_application()