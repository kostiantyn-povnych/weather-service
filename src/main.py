from fastapi import FastAPI

from weather.router import router


def fastApiApp():
    app = FastAPI(
        title="Simple Weather Service",
        version="0.1.0",
        docs_url="/docs",  # Swagger UI
        redoc_url="/redoc",  # ReDoc
    )

    # Include the weather router
    app.include_router(router, prefix="/api/v1")

    return app


app = fastApiApp()
