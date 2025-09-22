import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

from weather_service.api.caching import init_cache
from weather_service.api.rate_limiting import init_rate_limiting
from weather_service.api.weather import router as weather_router
from weather_service.core.exceptions import BaseServiceException

LOGGER = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    LOGGER.info("Entering FastAPi application lifespan")

    init_cache()

    yield

    LOGGER.info("Exiting FastAPI application lifespan")


def fastApiApp():
    app = FastAPI(
        title="Simple Weather Service",
        version="0.1.0",
        docs_url="/docs",  # Swagger UI
        redoc_url="/redoc",  # ReDoc
        lifespan=lifespan,
    )

    init_rate_limiting(app)

    @app.exception_handler(BaseServiceException)
    async def handle_service_layer_exception(
        request: Request, exc: BaseServiceException
    ):
        return PlainTextResponse(
            exc.message,
            status_code=exc.status_code,
        )

    # Include the weather router
    app.include_router(weather_router, prefix="/api/v1")

    return app


app = fastApiApp()
