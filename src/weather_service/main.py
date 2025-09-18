from fastapi import FastAPI


def fastApiApp():
    app = FastAPI(
        title="Simple Weather Service",
        version="0.1.0",
        docs_url="/docs",  # Swagger UI
        redoc_url="/redoc",  # ReDoc
    )
    return app


app = fastApiApp()
