"""
Создание FastAPI-приложения и подключение маршрутов.
"""

from fastapi import FastAPI
from server.api import routes
from server.storage.database import SessionLocal
from server.auth.auth_service import create_default_admin


def create_app(orchestrator=None) -> FastAPI:
    app = FastAPI(
        title="GTU Analysis API",
        description="API системы анализа данных газотурбинной установки",
        version="1.0.0",
    )

    app.include_router(routes.router)

    @app.on_event("startup")
    def on_startup():
        db = SessionLocal()
        try:
            create_default_admin(db)
        finally:
            db.close()

    if orchestrator:
        app.state.orchestrator = orchestrator

    return app
