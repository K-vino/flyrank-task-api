# FlyRank Task API (FastAPI + SQLite)

A lightweight, persistent Task Management CRUD API built with **FastAPI** and **SQLite** for FlyRank Backend AI Engineering (Week 3 - Assignment A2).

---

## 📌 Architecture Overview

```
Client (HTTP / Swagger UI)
       │
       ▼
   FastAPI Layer  (main.py)
       │
       ▼
 SQL Storage Layer (database.py)
       │
       ▼
 SQLite Database File (tasks.db)
```

Unlike in-memory data structures, data stored in **SQLite** persists across server restarts.

---

## ❓ Why SQLite?

- **Zero Configuration**: SQLite requires no separate server processes or complex setup.
- **Single File Storage**: All data is stored in a single file (`tasks.db`), making local development simple and portable.
- **ACID Compliant**: Provides full relational database transactions and reliability.
- **Separation of Concerns**: Keeps the API contract independent from the underlying persistence layer.

---

## 📁 Database Details

- **Database File**: `tasks.db` (located at project root)
- **Table Name**: `tasks`
- **Schema**:
  - `id` (`INTEGER PRIMARY KEY AUTOINCREMENT`)
  - `title` (`TEXT NOT NULL`)
  - `done` (`BOOLEAN NOT NULL DEFAULT 0`)

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed

### 2. Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install fastapi uvicorn
```

### 4. Run the Server
```bash
python -m uvicorn main:app --reload
```
The server will start at `http://127.0.0.1:8000`.

---

## 📡 API Endpoints

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | API Root / Welcome | `200 OK` |
| `GET` | `/tasks` | List all tasks (Optional filters: `search`, `done`) | `200 OK` |
| `GET` | `/tasks/{id}` | Get task by ID | `200 OK` / `404 Not Found` |
| `POST` | `/tasks` | Create a new task | `201 Created` / `400 Bad Request` |
| `PUT` | `/tasks/{id}` | Update task title / completion status | `200 OK` / `404` / `400` |
| `DELETE`| `/tasks/{id}` | Delete task by ID | `200 OK` / `404 Not Found` |
| `GET` | `/stats` | Get aggregate task statistics | `200 OK` |

Interactive API Documentation is available at `http://127.0.0.1:8000/docs`.

---

## 🔍 Manual SQL Exploration & Database Viewer

Using SQLite viewers (such as **DB Browser for SQLite** or VS Code SQLite extension):

### DB Viewer Interface Representation
```
+----+---------------------------+------+
| id | title                     | done |
+----+---------------------------+------+
| 1  | Learn SQLite              | 0    |
| 2  | Connect FastAPI to SQLite | 0    |
| 3  | Build CRUD API            | 1    |
+----+---------------------------+------+
```

### Example SQL Queries Executed
```sql
-- 1. List every task
SELECT * FROM tasks;

-- 2. Show only completed tasks
SELECT * FROM tasks WHERE done = 1;

-- 3. Count all tasks
SELECT COUNT(*) FROM tasks;

-- 4. Mark all tasks as completed
UPDATE tasks SET done = 1;

-- 5. Delete completed tasks
DELETE FROM tasks WHERE done = 1;
```

---

## 🧪 Testing

Run automated tests to verify CRUD persistence & response status codes:
```powershell
python -c "from fastapi.testclient import TestClient; from main import app; client = TestClient(app); print(client.get('/tasks').json())"
```
