from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.core.metrics import PrometheusMiddleware, metrics_json
from fastapi import FastAPI
from app.api import api_router
from app.core.events import on_startup
from app.core.exceptions import (
    http_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)

app = FastAPI(title="Phonebook App", version="0.1.0")
app.include_router(api_router)

app.add_middleware(PrometheusMiddleware)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.add_event_handler("startup", on_startup)

@app.get("/metrics/json")
def metrics_json_endpoint():
    return metrics_json()
