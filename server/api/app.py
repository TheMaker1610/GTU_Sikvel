"""
Создание FastAPI-приложения и подключение маршрутов.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from server.api import routes
from server.storage.database import SessionLocal
from server.auth.auth_service import create_default_admin


def create_app(orchestrator=None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        db = SessionLocal()
        try:
            create_default_admin(db)
        finally:
            db.close()
        yield

    app = FastAPI(
        title="GTU Analysis API",
        description="API системы анализа данных газотурбинной установки",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.include_router(routes.router)

    if orchestrator:
        app.state.orchestrator = orchestrator

    return app
