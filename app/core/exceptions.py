from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.core.logger import get_logger

logger = get_logger("exceptions","DEBUG")


async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException: {exc.status_code} - {exc.detail} - path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.exception(f"Database error: {str(exc)} - path: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error: Database operation failed."}
    )

async def general_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unexpected error: {str(exc)} - path: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error: An unexpected error occurred."}
    )
