from pydantic import BaseModel, Field
from typing import Optional


class TaskBase(BaseModel):
    title: str = Field(..., description="Task title")
    done: bool = Field(default=False, description="Task completion status")


class TaskCreate(BaseModel):
    title: str = Field(..., description="Task title")
    done: bool = Field(default=False, description="Task completion status")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, description="Task title")
    done: Optional[bool] = Field(default=None, description="Task completion status")


class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool

    class Config:
        from_attributes = True
