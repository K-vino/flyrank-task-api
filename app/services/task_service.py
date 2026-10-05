from typing import List, Optional
from app.repositories.interface import TaskRepositoryInterface
from app.models.task import TaskResponse, TaskCreate, TaskUpdate


class TaskService:

    def __init__(self, repository: TaskRepositoryInterface):
        self.repository = repository

    def get_all_tasks(
        self, search: Optional[str] = None, done: Optional[bool] = None
    ) -> List[TaskResponse]:
        return self.repository.get_all_tasks(search=search, done=done)

    def get_task_by_id(self, task_id: int) -> Optional[TaskResponse]:
        return self.repository.get_task_by_id(task_id)

    def create_task(self, task_data: TaskCreate) -> TaskResponse:
        title = task_data.title.strip()
        if not title:
            raise ValueError("Title is required and cannot be empty")
        return self.repository.create_task(title=title, done=task_data.done)

    def update_task(
        self, task_id: int, task_data: TaskUpdate
    ) -> Optional[TaskResponse]:
        if task_data.title is not None:
            stripped = task_data.title.strip()
            if not stripped:
                raise ValueError("Title cannot be empty")
            title = stripped
        else:
            title = None

        return self.repository.update_task(
            task_id=task_id, title=title, done=task_data.done
        )

    def delete_task(self, task_id: int) -> bool:
        return self.repository.delete_task(task_id)

    def get_stats(self) -> dict:
        return self.repository.get_stats()
