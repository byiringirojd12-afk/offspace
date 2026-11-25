import uvicorn
from contextlib import asynccontextmanager
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


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
