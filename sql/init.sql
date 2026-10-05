-- PostgreSQL Database Initialization Script for FlyRank Task API (BE-04)

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);

-- Seed 3 initial example tasks only if the table is empty
INSERT INTO tasks (title, done)
SELECT 'Learn SQLite', FALSE
WHERE NOT EXISTS (SELECT 1 FROM tasks);

INSERT INTO tasks (title, done)
SELECT 'Connect FastAPI to SQLite', FALSE
WHERE (SELECT COUNT(*) FROM tasks) = 1;

INSERT INTO tasks (title, done)
SELECT 'Build CRUD API', TRUE
WHERE (SELECT COUNT(*) FROM tasks) = 2;
