import os
import time
from typing import Optional

from fastapi import FastAPI, Query, Response
from prometheus_client import (
    Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency"
)

app = FastAPI(
    title="Tiny Service",
    description="A minimal Python service for Kubernetes deployment",
    version="1.0.0",
)

# Welcome prefix from environment variable for demonstrating secrets
WELCOME_PREFIX = os.getenv("WELCOME_PREFIX", "Hello")


@app.middleware("http")
async def metrics_middleware(request, call_next):
    """Middleware to collect metrics for all requests"""
    start_time = time.time()

    response = await call_next(request)

    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method, endpoint=request.url.path
    ).inc()
    REQUEST_LATENCY.observe(time.time() - start_time)

    return response


@app.get("/healthz")
async def health_check():
    """Health check endpoint for liveness and readiness probes"""
    return {"status": "ok", "timestamp": time.time()}


@app.get("/greet")
async def greet(name: Optional[str] = Query(None)):
    """Greeting endpoint that returns a JSON response"""
    if not name:
        return {
            "message": f"{WELCOME_PREFIX}, anonymous user!",
            "timestamp": time.time(),
        }

    return {
        "message": f"{WELCOME_PREFIX}, {name}!",
        "timestamp": time.time()
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "tiny-service",
        "version": "1.0.0",
        "endpoints": ["/healthz", "/greet", "/metrics"],
        "timestamp": time.time()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
