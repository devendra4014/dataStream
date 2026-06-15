from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings

# from app.schemas.connection_settings import DuckDBSettings
from app.database.db import DuckDBClient, DuckDBSettings
from app.middleware.logger_middleware import logging_middleware
from app.routers import auth
from app.services.auth_service import AuthService
from app.utils.logger import configure_logging, get_logger

# from app.database.duckdb_database import engine

configure_logging(level=settings.log_level)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app_starting")
    db_config = DuckDBSettings(database_url=settings.db_url)
    db = DuckDBClient(db_config)

    auth_service = AuthService(database=db)

    app.state.database = db
    app.state.auth_service = auth_service

    yield

    app.state.duckdb_client.is_connected()

    try:
        yield
    finally:
        logger.info("app_shutting_down")


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",  # Default port for Vite React apps
    "http://localhost:3000",  # Default port for Create React App
]

# adds middleware implemented as a class
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# add middleware implemented as a function
app.middleware("http")(logging_middleware)

# add routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])


@app.get("/hello")
async def hello():
    logger.info("hello_endpoint_called")
    return {"message": "Hello World"}
