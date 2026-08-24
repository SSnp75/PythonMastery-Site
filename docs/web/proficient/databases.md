---
title: Database Programming
description: sqlite3, PostgreSQL, connection pooling, transactions, migrations and patterns
---

# Database Programming <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🌐 Web & APIs Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="../../core/competent/error-handling/">Error Handling</a></span>
  </div>
</div>

---

## sqlite3 (built-in) — complete guide

### CRUD operations

```python
import sqlite3

# Connect (creates file if not exists)
conn = sqlite3.connect("app.db")
conn.row_factory = sqlite3.Row   # access columns by name

cursor = conn.cursor()

# ─── CREATE TABLE ─────────────────────────────────
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        age INTEGER CHECK(age >= 0),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# ─── INSERT (parameterized — prevents SQL injection!) ─
cursor.execute(
    "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
    ("Alice", "alice@example.com", 30)
)

# Insert many rows
users = [
    ("Bob", "bob@example.com", 25),
    ("Charlie", "charlie@example.com", 35),
    ("Diana", "diana@example.com", 28),
]
cursor.executemany(
    "INSERT INTO users (name, email, age) VALUES (?, ?, ?)", users
)

# ─── SELECT ───────────────────────────────────────
cursor.execute("SELECT * FROM users WHERE age > ?", (26,))
for row in cursor.fetchall():
    print(f"{row['name']} ({row['email']}) - age {row['age']}")
# Output:
# Alice (alice@example.com) - age 30
# Charlie (charlie@example.com) - age 35
# Diana (diana@example.com) - age 28

# Single row
cursor.execute("SELECT * FROM users WHERE id = ?", (1,))
user = cursor.fetchone()
print(dict(user))   # {'id': 1, 'name': 'Alice', ...}

# ─── UPDATE ───────────────────────────────────────
cursor.execute(
    "UPDATE users SET age = ? WHERE name = ?", (31, "Alice")
)
print(f"Rows affected: {cursor.rowcount}")   # 1

# ─── DELETE ───────────────────────────────────────
cursor.execute("DELETE FROM users WHERE name = ?", ("Bob",))

conn.commit()
conn.close()
```

### Context manager pattern

```python
from contextlib import contextmanager

@contextmanager
def get_db(path="app.db"):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # better concurrency
    conn.execute("PRAGMA foreign_keys=ON")    # enforce FK constraints
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

# Usage
with get_db() as db:
    db.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
               ("Eve", "eve@example.com", 22))
    # Auto-commits on success, auto-rolls back on exception
```

### Transactions

```python
with get_db() as db:
    try:
        db.execute("BEGIN")
        db.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
        db.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
        db.execute("COMMIT")
    except Exception:
        db.execute("ROLLBACK")
        raise
```

---

## PostgreSQL with psycopg (v3)

```python
import psycopg
from psycopg.rows import dict_row

# ─── Connection ───────────────────────────────────
conn = psycopg.connect(
    "postgresql://user:pass@localhost:5432/mydb",
    row_factory=dict_row,
)

# ─── Queries with named parameters ───────────────
with conn.cursor() as cur:
    cur.execute(
        "SELECT * FROM users WHERE age > %(min_age)s AND city = %(city)s",
        {"min_age": 25, "city": "NYC"},
    )
    users = cur.fetchall()
    for user in users:
        print(user["name"], user["email"])

conn.commit()
conn.close()
```

### Connection pooling

```python
from psycopg_pool import ConnectionPool

pool = ConnectionPool(
    "postgresql://user:pass@localhost/mydb",
    min_size=5,
    max_size=20,
)

def get_users():
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM users")
            return cur.fetchall()

# Pool handles connection reuse, health checks, etc.
```

### Async PostgreSQL

```python
import asyncio
import psycopg
from psycopg.rows import dict_row

async def get_user(user_id: int):
    async with await psycopg.AsyncConnection.connect(
        "postgresql://user:pass@localhost/mydb",
        row_factory=dict_row,
    ) as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return await cur.fetchone()
```

---

## Query patterns

### Parameterized queries (ALWAYS use these)

```python
# SAFE — parameterized
cursor.execute("SELECT * FROM users WHERE name = ?", (user_input,))

# DANGEROUS — string formatting (SQL injection!)
cursor.execute(f"SELECT * FROM users WHERE name = '{user_input}'")   # NEVER!
```

### Bulk operations

```python
# executemany — efficient batch insert
data = [(f"user_{i}", f"user{i}@example.com", 20 + i) for i in range(10000)]

with get_db() as db:
    db.executemany(
        "INSERT INTO users (name, email, age) VALUES (?, ?, ?)", data
    )
# Much faster than 10000 individual inserts
```

### Full-text search (SQLite FTS5)

```python
with get_db() as db:
    db.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts
        USING fts5(title, content)
    """)

    db.execute(
        "INSERT INTO articles_fts (title, content) VALUES (?, ?)",
        ("Python Tips", "Learn decorators and generators...")
    )

    # Search
    results = db.execute(
        "SELECT * FROM articles_fts WHERE articles_fts MATCH ?",
        ("decorators",)
    ).fetchall()
```

---

## Schema migrations

### Manual approach

```python
MIGRATIONS = [
    """CREATE TABLE IF NOT EXISTS schema_version (version INTEGER)""",
    """INSERT INTO schema_version VALUES (0)""",
    """ALTER TABLE users ADD COLUMN phone TEXT""",
    """CREATE INDEX idx_users_email ON users(email)""",
]

def migrate(db):
    db.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER DEFAULT 0)")
    row = db.execute("SELECT MAX(version) as v FROM schema_version").fetchone()
    current = row["v"] or 0

    for i, sql in enumerate(MIGRATIONS[current:], start=current):
        print(f"  Applying migration {i + 1}...")
        db.execute(sql)
        db.execute("UPDATE schema_version SET version = ?", (i + 1,))

    db.commit()
```

---

## Practice Exercises

1. **Build a complete CRUD module** for a `tasks` table with proper error handling and transactions.
2. **Implement connection pooling** for a multi-threaded application.
3. **Write a migration system** that applies `.sql` files in order.
4. **Build a full-text search** feature for a blog using SQLite FTS5.
5. **Compare performance** of individual inserts vs `executemany` vs COPY (PostgreSQL) for 100K rows.
6. **Implement soft-delete** (set `deleted_at` timestamp instead of actually deleting).
