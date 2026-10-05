import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes import auth, public, protected, tasks
from app.repositories.postgres_task_repository import PostgresTaskRepository
from app.services.task_service import TaskService

logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Server starting up...")
    yield
    logger.info("Server shutting down...")


app = FastAPI(
    title="Containerized Task & Auth API",
    description="FastAPI CRUD & Supabase Auth API with PostgreSQL & Docker",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Invalid input parameters or missing required fields"},
    )


# Include Routers
app.include_router(auth.router)
app.include_router(public.router)
app.include_router(protected.router)
app.include_router(tasks.router)


@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to FlyRank Containerized Task & Auth API!",
        "docs": "/docs",
    }


@app.get("/stats", tags=["Tasks"])
def get_stats():
    repo = PostgresTaskRepository()
    service = TaskService(repository=repo)
    return service.get_stats()
