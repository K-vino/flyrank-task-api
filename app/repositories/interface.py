from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.task import TaskResponse


class TaskRepositoryInterface(ABC):

    @abstractmethod
    def get_all_tasks(
        self, search: Optional[str] = None, done: Optional[bool] = None
    ) -> List[TaskResponse]:
        pass

    @abstractmethod
    def get_task_by_id(self, task_id: int) -> Optional[TaskResponse]:
        pass

    @abstractmethod
    def create_task(self, title: str, done: bool = False) -> TaskResponse:
        pass

    @abstractmethod
    def update_task(
        self, task_id: int, title: Optional[str] = None, done: Optional[bool] = None
    ) -> Optional[TaskResponse]:
        pass

    @abstractmethod
    def delete_task(self, task_id: int) -> bool:
        pass

    @abstractmethod
    def get_stats(self) -> dict:
        pass
