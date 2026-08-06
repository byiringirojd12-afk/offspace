from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from backend.api.errors import APIError, AuthenticationError
from backend.config.settings import settings
from backend.logs.logger import logger


def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Incoming request {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Completed request {request.method} {request.url} status={response.status_code}")
        return response


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error for request {request.url}: {exc}")
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content={"success": False, "error": "Validation failed", "details": exc.errors(), "status_code": HTTP_422_UNPROCESSABLE_ENTITY},
        )

    @app.exception_handler(AuthenticationError)
    async def authentication_exception_handler(request: Request, exc: AuthenticationError):
        logger.warning(f"Authentication failed for request {request.url}: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.message, "code": exc.code, "status_code": exc.status_code},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(f"HTTP exception for request {request.url}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.detail, "code": exc.__class__.__name__, "status_code": exc.status_code},
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.exception(f"Database error during request {request.url}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Database failure", "code": "DATABASE_ERROR", "status_code": 500},
        )

    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        logger.warning(f"API error for request {request.url}: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": exc.message, "code": exc.code, "status_code": exc.status_code},
        )

    @app.exception_handler(Exception)
    async def internal_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception during request {request.url}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Internal server error", "code": "INTERNAL_SERVER_ERROR", "status_code": 500},
        )
