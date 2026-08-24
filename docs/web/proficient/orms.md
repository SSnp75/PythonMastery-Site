---
title: ORMs
description: SQLAlchemy 2.0, relationships, async, migrations and query optimization
---

# ORMs <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🌐 Web & APIs Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="databases/">Database Programming</a></span>
  </div>
</div>

---

## SQLAlchemy 2.0 — Declarative Models

```python
from sqlalchemy import create_engine, String, ForeignKey, func
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column,
    relationship, Session, sessionmaker
)
from datetime import datetime

# ─── Engine ───────────────────────────────────────
engine = create_engine("sqlite:///app.db", echo=False)

# ─── Base class ───────────────────────────────────
class Base(DeclarativeBase):
    pass

# ─── Models ───────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # Relationship — one user has many posts
    posts: Mapped[list["Post"]] = relationship(back_populates="author", cascade="all, delete-orphan")

    def __repr__(self):
        return f"User(id={self.id}, name={self.name!r})"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str]
    published: Mapped[bool] = mapped_column(default=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relationship — back reference
    author: Mapped["User"] = relationship(back_populates="posts")
    tags: Mapped[list["Tag"]] = relationship(secondary="post_tags", back_populates="posts")

    def __repr__(self):
        return f"Post(id={self.id}, title={self.title!r})"


# Many-to-many association table
from sqlalchemy import Table, Column, Integer

post_tags = Table(
    "post_tags", Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    posts: Mapped[list["Post"]] = relationship(secondary="post_tags", back_populates="tags")


# Create all tables
Base.metadata.create_all(engine)
```

---

## CRUD operations

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

SessionLocal = sessionmaker(bind=engine)

# ─── CREATE ───────────────────────────────────────
with Session(engine) as session:
    user = User(name="Alice", email="alice@example.com")
    session.add(user)

    post = Post(title="First Post", content="Hello World!", author=user)
    session.add(post)

    session.commit()
    print(f"Created user {user.id} and post {post.id}")

# ─── READ (select) ───────────────────────────────
with Session(engine) as session:
    # Get by primary key
    user = session.get(User, 1)
    print(user)   # User(id=1, name='Alice')

    # Query with filter
    stmt = select(User).where(User.name == "Alice")
    alice = session.scalars(stmt).first()

    # All users
    all_users = session.scalars(select(User)).all()

    # Complex query
    stmt = (
        select(Post)
        .where(Post.published == True)
        .order_by(Post.created_at.desc())
        .limit(10)
    )
    posts = session.scalars(stmt).all()

    # Join
    stmt = (
        select(Post)
        .join(User)
        .where(User.name == "Alice")
    )
    alice_posts = session.scalars(stmt).all()

# ─── UPDATE ───────────────────────────────────────
with Session(engine) as session:
    user = session.get(User, 1)
    user.name = "Alice Smith"   # just modify the object
    session.commit()            # changes detected and saved

    # Bulk update
    from sqlalchemy import update
    session.execute(
        update(Post).where(Post.author_id == 1).values(published=True)
    )
    session.commit()

# ─── DELETE ───────────────────────────────────────
with Session(engine) as session:
    user = session.get(User, 1)
    session.delete(user)   # cascades to posts (cascade="all, delete-orphan")
    session.commit()
```

---

## Eager vs Lazy Loading

```python
from sqlalchemy.orm import selectinload, joinedload, lazyload

# LAZY loading (default) — N+1 problem!
with Session(engine) as session:
    users = session.scalars(select(User)).all()
    for user in users:
        print(user.posts)   # each access = separate SQL query!

# EAGER loading — one query for all
with Session(engine) as session:
    # selectinload — separate IN query (good for collections)
    stmt = select(User).options(selectinload(User.posts))
    users = session.scalars(stmt).all()
    for user in users:
        print(user.posts)   # no extra queries!

    # joinedload — single JOIN query (good for single relationships)
    stmt = select(Post).options(joinedload(Post.author))
    posts = session.scalars(stmt).all()
    for post in posts:
        print(post.author.name)   # already loaded
```

---

## Async SQLAlchemy

```python
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession, async_sessionmaker
)

async_engine = create_async_engine("sqlite+aiosqlite:///app.db")
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession)

async def get_user(user_id: int) -> User | None:
    async with AsyncSessionLocal() as session:
        return await session.get(User, user_id)

async def create_user(name: str, email: str) -> User:
    async with AsyncSessionLocal() as session:
        user = User(name=name, email=email)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

# With FastAPI
from fastapi import Depends

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/users/{user_id}")
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404)
    return user
```

---

## Alembic — database migrations

```bash
# Initialize
pip install alembic
alembic init migrations

# Configure alembic.ini → set sqlalchemy.url
# Configure migrations/env.py → import your Base.metadata
```

```python
# migrations/env.py (key part)
from myapp.models import Base
target_metadata = Base.metadata
```

```bash
# Generate migration from model changes
alembic revision --autogenerate -m "Add phone column to users"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# Show current state
alembic current
alembic history
```

Generated migration file:
```python
# migrations/versions/abc123_add_phone_column.py
def upgrade():
    op.add_column("users", sa.Column("phone", sa.String(20)))

def downgrade():
    op.drop_column("users", "phone")
```

---

## Query optimization patterns

### Avoiding N+1

```python
# BAD — N+1 queries (1 query for users + N queries for posts)
users = session.scalars(select(User)).all()
for user in users:
    print(len(user.posts))   # each triggers a SELECT

# GOOD — 2 queries total (1 for users, 1 IN query for all posts)
users = session.scalars(
    select(User).options(selectinload(User.posts))
).all()
```

### Selecting only needed columns

```python
# Instead of loading full objects:
stmt = select(User.name, User.email).where(User.age > 25)
results = session.execute(stmt).all()
# Returns lightweight tuples, not full User objects
```

### Pagination

```python
def paginate(session, query, page: int, per_page: int = 20):
    total = session.scalar(select(func.count()).select_from(query.subquery()))
    items = session.scalars(
        query.offset((page - 1) * per_page).limit(per_page)
    ).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": (total + per_page - 1) // per_page,
    }
```

---

## Practice Exercises

1. **Build a blog system** with User, Post, Comment, Tag models and proper relationships.
2. **Implement soft-delete** — add `deleted_at` field and filter it in all queries.
3. **Set up Alembic** and create/apply 5 incremental migrations.
4. **Demonstrate N+1** — show the problem and fix with `selectinload`.
5. **Build an async repository** pattern with SQLAlchemy + FastAPI.
6. **Write a query** that finds the top 5 authors by post count using `GROUP BY` and `func.count`.
