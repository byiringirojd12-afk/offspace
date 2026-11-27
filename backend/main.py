import sys
import threading
from contextlib import asynccontextmanager
from typing import TextIO

import uvicorn
from fastapi import FastAPI

from backend.api.router import api_router
from backend.api.middleware import setup_middlewares, setup_exception_handlers, RequestLoggingMiddleware
from backend.config.settings import settings
from backend.database import engine
from backend.database.models import Base
from backend.logs.logger import logger
from sqlalchemy import text


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Offspace backend")
    try:
        Base.metadata.create_all(bind=engine)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        logger.exception("Database connection failed during startup")
        raise
    yield
    logger.info("Shutting down Offspace backend")
    engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.api_version,
        debug=settings.debug,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    setup_middlewares(app)
    setup_exception_handlers(app)
    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(api_router)

    return app


app = create_app()


def _watch_parent_shutdown(
    server: uvicorn.Server, control_stream: TextIO
) -> None:
    try:
        for line in control_stream:
            if line.strip() == "OFFSPACE_SHUTDOWN":
                logger.info("Backend shutdown requested by desktop process")
                server.should_exit = True
                return
    except (OSError, ValueError):
        logger.exception("Backend control pipe failed; requesting shutdown")
        server.should_exit = True
        return

    logger.info("Backend control pipe closed; requesting shutdown")
    server.should_exit = True


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = uvicorn.Server(
        uvicorn.Config(app, host=host, port=port, reload=False)
    )
    control_stream = sys.stdin
    if control_stream is not None and not control_stream.isatty():
        threading.Thread(
            target=_watch_parent_shutdown,
            args=(server, control_stream),
            daemon=True,
            name="offspace-parent-control",
        ).start()
    server.run()


if __name__ == "__main__":
    run_server()
