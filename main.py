from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from database import create_database, get_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database and seed initial example tasks if empty
    create_database()
    yield


app = FastAPI(
    title="Task API",
    description="FastAPI Task CRUD API powered by SQLite",
    lifespan=lifespan,
)


# Also ensure create_database runs on module import for safety
create_database()


# Custom exception handler for 422 validation errors to format as 400
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Title is required and must be a non-empty string"},
    )


class TaskCreate(BaseModel):
    title: str = Field(..., description="Task title")
    done: bool = Field(default=False, description="Completion status")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, description="Task title")
    done: Optional[bool] = Field(default=None, description="Completion status")


@app.get("/")
def read_root():
    return {"message": "Welcome to Task API backed by SQLite!"}


@app.get("/tasks")
def get_tasks(
    search: Optional[str] = None,
    done: Optional[bool] = None,
):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT id, title, done FROM tasks WHERE 1=1"
    params = []

    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")

    if done is not None:
        query += " AND done = ?"
        params.append(1 if done else 0)

    query += " ORDER BY id ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    tasks = [
        {"id": row["id"], "title": row["title"], "done": bool(row["done"])}
        for row in rows
    ]
    return tasks


@app.get("/stats")
def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS total, SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END) AS completed FROM tasks")
    row = cursor.fetchone()
    conn.close()

    total = row["total"] or 0
    completed = row["completed"] or 0
    pending = total - completed

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
    }


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Task not found"},
        )

    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    title = task.title.strip()
    if not title:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Title is required and cannot be empty"},
        )

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (title, 1 if task.done else 0),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {"id": new_id, "title": title, "done": task.done}


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    existing = cursor.fetchone()

    if existing is None:
        conn.close()
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Task not found"},
        )

    new_title = existing["title"]
    if task.title is not None:
        stripped = task.title.strip()
        if not stripped:
            conn.close()
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Title cannot be empty"},
            )
        new_title = stripped

    new_done = existing["done"] if task.done is None else (1 if task.done else 0)

    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, task_id),
    )
    conn.commit()
    conn.close()

    return {"id": task_id, "title": new_title, "done": bool(new_done)}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    existing = cursor.fetchone()

    if existing is None:
        conn.close()
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Task not found"},
        )

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return {"message": "Task deleted successfully"}
