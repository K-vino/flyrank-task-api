from typing import List, Optional
from fastapi import APIRouter, Depends, status, Response
from fastapi.responses import JSONResponse
from app.models.task import TaskCreate, TaskUpdate, TaskResponse
from app.repositories.postgres_task_repository import PostgresTaskRepository
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_task_service() -> TaskService:
    repo = PostgresTaskRepository()
    return TaskService(repository=repo)


@router.get("", response_model=List[TaskResponse], status_code=status.HTTP_200_OK)
def get_tasks(
    search: Optional[str] = None,
    done: Optional[bool] = None,
    service: TaskService = Depends(get_task_service),
):
    return service.get_all_tasks(search=search, done=done)


@router.get("/{task_id}", status_code=status.HTTP_200_OK)
def get_task_by_id(
    task_id: int,
    service: TaskService = Depends(get_task_service),
):
    task = service.get_task_by_id(task_id)
    if not task:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Task not found"},
        )
    return task


@router.post("", status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    service: TaskService = Depends(get_task_service),
):
    try:
        task = service.create_task(payload)
        return task
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)},
        )


@router.put("/{task_id}", status_code=status.HTTP_200_OK)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    service: TaskService = Depends(get_task_service),
):
    try:
        updated = service.update_task(task_id, payload)
        if not updated:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": "Task not found"},
            )
        return updated
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)},
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
):
    deleted = service.delete_task(task_id)
    if not deleted:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Task not found"},
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
