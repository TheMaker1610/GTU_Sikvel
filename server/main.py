"""
Точка входа серверной части.
Запускает оркестратор и FastAPI-сервер.
"""
import asyncio
import uvicorn
from server.orchestrator.orchestrator import Orchestrator
from server.api.app import create_app
from server.storage.database import init_db
from server.logging_service.logger import get_logger
from server.config.settings import SERVER_HOST, SERVER_PORT

logger = get_logger(__name__)


async def main():
    logger.info("Инициализация базы данных...")
    init_db()

    orchestrator = Orchestrator()

    app = create_app(orchestrator)

    config = uvicorn.Config(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info",
    )
    server = uvicorn.Server(config)

    logger.info(f"Запуск сервера на {SERVER_HOST}:{SERVER_PORT}")
    await asyncio.gather(
        orchestrator.run(),
        server.serve(),
    )


if __name__ == "__main__":
    asyncio.run(main())
