from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST
)
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

custom_registry = CollectorRegistry()

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint"],
    registry=custom_registry
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "Duration of HTTP requests in seconds",
    ["endpoint"],
    registry=custom_registry
)

contacts_total = Gauge(
    "contacts_total",
    "Current total number of contacts in the database",
    registry=custom_registry
)

cache_requests_total = Counter(
    "cache_requests_total",
    "Total cache checks",
    ["endpoint"],
    registry=custom_registry
)

cache_hits_total = Counter(
    "cache_hits_total",
    "Cache hits",
    ["endpoint"],
    registry=custom_registry
)

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        endpoint = request.url.path
        method = request.method
        http_requests_total.labels(method=method, endpoint=endpoint).inc()
        http_request_duration_seconds.labels(endpoint=endpoint).observe(duration)
        return response

def metrics_endpoint():
    return Response(generate_latest(custom_registry), media_type=CONTENT_TYPE_LATEST)

def metrics_json():
    metrics_data = {}
    for metric in custom_registry.collect():
        samples = []
        for sample in metric.samples:
            samples.append({
                "name": sample.name,
                "labels": sample.labels,
                "value": sample.value
            })
        metrics_data[metric.name] = {
            "type": metric.type,
            "help": metric.documentation,
            "samples": samples
        }
    return metrics_data
