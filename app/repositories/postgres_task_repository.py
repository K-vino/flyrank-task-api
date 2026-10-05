import os
import sqlite3
from typing import List, Optional
from app.repositories.interface import TaskRepositoryInterface
from app.models.task import TaskResponse

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False


class PostgresTaskRepository(TaskRepositoryInterface):

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", "postgresql://postgres:postgres@db:5432/tasks"
        )
        self.use_postgres = HAS_PSYCOPG2 and self.database_url.startswith("postgresql")

    def _get_connection(self):
        if self.use_postgres:
            try:
                conn = psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
                return conn, True
            except Exception:
                # Fallback to local SQLite if PostgreSQL service is unavailable locally
                pass

        # SQLite fallback
        conn = sqlite3.connect("tasks.db")
        conn.row_factory = sqlite3.Row
        return conn, False

    def _init_sqlite_if_needed(self, conn):
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        cursor.execute("SELECT COUNT(*) FROM tasks")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [
                    ("Learn SQLite", 0),
                    ("Connect FastAPI to SQLite", 0),
                    ("Build CRUD API", 1),
                ],
            )
        conn.commit()

    def get_all_tasks(
        self, search: Optional[str] = None, done: Optional[bool] = None
    ) -> List[TaskResponse]:
        conn, is_pg = self._get_connection()
        cursor = conn.cursor()

        if is_pg:
            query = "SELECT id, title, done FROM tasks WHERE 1=1"
            params = []
            if search:
                query += " AND title ILIKE %s"
                params.append(f"%{search}%")
            if done is not None:
                query += " AND done = %s"
                params.append(done)
            query += " ORDER BY id ASC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            return [
                TaskResponse(id=row["id"], title=row["title"], done=bool(row["done"]))
                for row in rows
            ]
        else:
            self._init_sqlite_if_needed(conn)
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
            return [
                TaskResponse(id=row["id"], title=row["title"], done=bool(row["done"]))
                for row in rows
            ]

    def get_task_by_id(self, task_id: int) -> Optional[TaskResponse]:
        conn, is_pg = self._get_connection()
        cursor = conn.cursor()
        placeholder = "%s" if is_pg else "?"
        cursor.execute(f"SELECT id, title, done FROM tasks WHERE id = {placeholder}", (task_id,))
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None
        return TaskResponse(id=row["id"], title=row["title"], done=bool(row["done"]))

    def create_task(self, title: str, done: bool = False) -> TaskResponse:
        conn, is_pg = self._get_connection()
        cursor = conn.cursor()

        if is_pg:
            cursor.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done",
                (title, done),
            )
            row = cursor.fetchone()
            conn.commit()
            conn.close()
            return TaskResponse(id=row["id"], title=row["title"], done=bool(row["done"]))
        else:
            self._init_sqlite_if_needed(conn)
            cursor.execute(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                (title, 1 if done else 0),
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return TaskResponse(id=new_id, title=title, done=done)

    def update_task(
        self, task_id: int, title: Optional[str] = None, done: Optional[bool] = None
    ) -> Optional[TaskResponse]:
        existing = self.get_task_by_id(task_id)
        if not existing:
            return None

        new_title = existing.title if title is None else title
        new_done = existing.done if done is None else done

        conn, is_pg = self._get_connection()
        cursor = conn.cursor()

        if is_pg:
            cursor.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s",
                (new_title, new_done, task_id),
            )
        else:
            cursor.execute(
                "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
                (new_title, 1 if new_done else 0, task_id),
            )

        conn.commit()
        conn.close()
        return TaskResponse(id=task_id, title=new_title, done=new_done)

    def delete_task(self, task_id: int) -> bool:
        existing = self.get_task_by_id(task_id)
        if not existing:
            return False

        conn, is_pg = self._get_connection()
        cursor = conn.cursor()
        placeholder = "%s" if is_pg else "?"
        cursor.execute(f"DELETE FROM tasks WHERE id = {placeholder}", (task_id,))
        conn.commit()
        conn.close()
        return True

    def get_stats(self) -> dict:
        conn, is_pg = self._get_connection()
        cursor = conn.cursor()
        if is_pg:
            cursor.execute(
                "SELECT COUNT(*) AS total, SUM(CASE WHEN done = TRUE THEN 1 ELSE 0 END) AS completed FROM tasks"
            )
        else:
            self._init_sqlite_if_needed(conn)
            cursor.execute(
                "SELECT COUNT(*) AS total, SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END) AS completed FROM tasks"
            )
        row = cursor.fetchone()
        conn.close()

        total = row["total"] or 0
        completed = row["completed"] or 0
        pending = total - completed
        return {"total": total, "completed": completed, "pending": pending}
