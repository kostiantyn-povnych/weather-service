import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from caching import init_cache
from common.exceptions import BaseServiceException
from telemetry import configure_logging
from weather.router import router

LOGGER = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    LOGGER.info("Entering FastAPi application lifespan")
    configure_logging()

    await init_cache(app)

    yield
    LOGGER.info("Exiting FastAPi application lifespan")


def handle_service_layer_exception(request: Request, exc: BaseServiceException):
    """Handle service layer exceptions and return appropriate HTTP status and message."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message, "error": exc.__class__.__name__},
    )


def fastApiApp():
    app = FastAPI(
        title="Simple Weather Service",
        version="0.1.0",
        docs_url="/docs",  # Swagger UI
        redoc_url="/redoc",  # ReDoc
        lifespan=lifespan,
    )

    @app.exception_handler(BaseServiceException)
    async def handle_service_layer_exception(
        request: Request, exc: BaseServiceException
    ):
        return PlainTextResponse(
            exc.message,
            status_code=exc.status_code,
        )

    # Include the weather router
    app.include_router(router, prefix="/api/v1")

    return app


app = fastApiApp()
