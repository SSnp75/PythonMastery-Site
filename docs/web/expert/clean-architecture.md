---
title: Clean Architecture
description: Layered design, dependency inversion, ports & adapters and testable systems
---

# Clean Architecture <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🌐 Web & APIs Track · Level 6</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="../proficient/frameworks/">Web Frameworks</a>, <a href="../proficient/orms/">ORMs</a></span>
  </div>
</div>

---

## The dependency rule

The core principle: **dependencies point inward**. Inner layers know nothing about outer layers.

```
┌─────────────────────────────────────────────┐
│             Frameworks & Drivers             │  ← FastAPI, SQLAlchemy, Redis
├─────────────────────────────────────────────┤
│            Interface Adapters                │  ← Controllers, Repositories
├─────────────────────────────────────────────┤
│              Use Cases                       │  ← Business logic
├─────────────────────────────────────────────┤
│               Entities                       │  ← Domain objects (center)
└─────────────────────────────────────────────┘
```

---

## Project structure

```
src/
├── domain/                  # Entities (innermost)
│   ├── entities.py
│   └── exceptions.py
├── application/             # Use cases
│   ├── interfaces.py        # Ports (abstract repos)
│   ├── create_user.py
│   └── get_user.py
├── infrastructure/          # Adapters (outermost)
│   ├── database/
│   │   ├── models.py
│   │   └── user_repository.py
│   ├── cache/
│   │   └── redis_cache.py
│   └── email/
│       └── smtp_sender.py
└── presentation/            # API layer
    ├── api/
    │   ├── routes.py
    │   └── schemas.py
    └── main.py
```

---

## Full implementation

### Layer 1: Domain (Entities)

```python
# domain/entities.py
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    id: int | None
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    def change_email(self, new_email: str) -> None:
        """Domain logic: validate email change."""
        if not new_email or "@" not in new_email:
            raise ValueError("Invalid email address")
        self.email = new_email

# domain/exceptions.py
class UserNotFoundError(Exception):
    def __init__(self, user_id: int):
        super().__init__(f"User {user_id} not found")
        self.user_id = user_id

class DuplicateEmailError(Exception):
    def __init__(self, email: str):
        super().__init__(f"Email {email} already registered")
        self.email = email
```

### Layer 2: Application (Use Cases + Ports)

```python
# application/interfaces.py
from typing import Protocol
from domain.entities import User

class UserRepository(Protocol):
    """Port — defines what the application NEEDS, not how it's done."""
    async def get_by_id(self, user_id: int) -> User | None: ...
    async def get_by_email(self, email: str) -> User | None: ...
    async def save(self, user: User) -> User: ...
    async def delete(self, user_id: int) -> None: ...

class EmailSender(Protocol):
    async def send_welcome(self, user: User) -> None: ...

class EventPublisher(Protocol):
    async def publish(self, event_type: str, data: dict) -> None: ...
```

```python
# application/create_user.py
from dataclasses import dataclass
from domain.entities import User
from domain.exceptions import DuplicateEmailError
from .interfaces import UserRepository, EmailSender, EventPublisher

@dataclass
class CreateUserRequest:
    name: str
    email: str

@dataclass
class CreateUserResponse:
    id: int
    name: str
    email: str

class CreateUser:
    """Use case: create a new user."""

    def __init__(
        self,
        user_repo: UserRepository,
        email_sender: EmailSender,
        events: EventPublisher,
    ):
        self.user_repo = user_repo
        self.email_sender = email_sender
        self.events = events

    async def execute(self, request: CreateUserRequest) -> CreateUserResponse:
        # Business rule: email must be unique
        existing = await self.user_repo.get_by_email(request.email)
        if existing:
            raise DuplicateEmailError(request.email)

        # Create domain entity
        user = User(id=None, name=request.name, email=request.email)

        # Persist
        saved_user = await self.user_repo.save(user)

        # Side effects
        await self.email_sender.send_welcome(saved_user)
        await self.events.publish("user.created", {"user_id": saved_user.id})

        return CreateUserResponse(
            id=saved_user.id,
            name=saved_user.name,
            email=saved_user.email,
        )
```

### Layer 3: Infrastructure (Adapters)

```python
# infrastructure/database/user_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from domain.entities import User
from .models import UserModel

class SQLAlchemyUserRepository:
    """Adapter: implements UserRepository using SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        model = await self.session.get(UserModel, user_id)
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        model = await self.session.scalar(stmt)
        return self._to_entity(model) if model else None

    async def save(self, user: User) -> User:
        model = UserModel(name=user.name, email=user.email)
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, user_id: int) -> None:
        model = await self.session.get(UserModel, user_id)
        if model:
            await self.session.delete(model)

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            name=model.name,
            email=model.email,
            created_at=model.created_at,
        )
```

```python
# infrastructure/email/smtp_sender.py
from domain.entities import User

class SmtpEmailSender:
    async def send_welcome(self, user: User) -> None:
        # Real implementation would send via SMTP
        print(f"Sending welcome email to {user.email}")

# For testing
class FakeEmailSender:
    def __init__(self):
        self.sent = []

    async def send_welcome(self, user: User) -> None:
        self.sent.append(("welcome", user.email))
```

### Layer 4: Presentation (API)

```python
# presentation/api/routes.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from application.create_user import CreateUser, CreateUserRequest
from domain.exceptions import DuplicateEmailError

router = APIRouter(prefix="/users", tags=["users"])

class UserCreateSchema(BaseModel):
    name: str
    email: EmailStr

class UserResponseSchema(BaseModel):
    id: int
    name: str
    email: str

@router.post("/", response_model=UserResponseSchema, status_code=201)
async def create_user(
    data: UserCreateSchema,
    use_case: CreateUser = Depends(get_create_user_use_case),
):
    try:
        result = await use_case.execute(
            CreateUserRequest(name=data.name, email=data.email)
        )
        return result
    except DuplicateEmailError as e:
        raise HTTPException(status_code=409, detail=str(e))
```

### Dependency Injection (wiring it together)

```python
# presentation/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.database.user_repository import SQLAlchemyUserRepository
from infrastructure.email.smtp_sender import SmtpEmailSender
from infrastructure.events.redis_publisher import RedisEventPublisher
from application.create_user import CreateUser

async def get_db_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session

def get_create_user_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> CreateUser:
    return CreateUser(
        user_repo=SQLAlchemyUserRepository(session),
        email_sender=SmtpEmailSender(),
        events=RedisEventPublisher(),
    )
```

---

## Testing — the real benefit

```python
# tests/test_create_user.py
import pytest
from application.create_user import CreateUser, CreateUserRequest
from domain.exceptions import DuplicateEmailError

class FakeUserRepo:
    def __init__(self):
        self.users = {}
        self.next_id = 1

    async def get_by_id(self, user_id):
        return self.users.get(user_id)

    async def get_by_email(self, email):
        return next((u for u in self.users.values() if u.email == email), None)

    async def save(self, user):
        user.id = self.next_id
        self.users[self.next_id] = user
        self.next_id += 1
        return user

    async def delete(self, user_id):
        self.users.pop(user_id, None)

class FakeEmailSender:
    def __init__(self):
        self.sent = []
    async def send_welcome(self, user):
        self.sent.append(user.email)

class FakeEvents:
    def __init__(self):
        self.published = []
    async def publish(self, event_type, data):
        self.published.append((event_type, data))


@pytest.mark.asyncio
async def test_create_user_success():
    repo = FakeUserRepo()
    email = FakeEmailSender()
    events = FakeEvents()
    use_case = CreateUser(repo, email, events)

    result = await use_case.execute(CreateUserRequest(name="Alice", email="a@b.com"))

    assert result.id == 1
    assert result.name == "Alice"
    assert email.sent == ["a@b.com"]
    assert events.published == [("user.created", {"user_id": 1})]

@pytest.mark.asyncio
async def test_create_user_duplicate_email():
    repo = FakeUserRepo()
    email = FakeEmailSender()
    events = FakeEvents()
    use_case = CreateUser(repo, email, events)

    await use_case.execute(CreateUserRequest(name="Alice", email="a@b.com"))

    with pytest.raises(DuplicateEmailError):
        await use_case.execute(CreateUserRequest(name="Bob", email="a@b.com"))
```

Notice: **zero database, zero HTTP, zero external services** — pure unit tests that run instantly.

---

## Practice Exercises

1. **Refactor a Flask/FastAPI app** into clean architecture layers.
2. **Add a `GetUser` use case** with caching (Redis adapter that can be swapped for in-memory).
3. **Write tests for every use case** using only fake implementations — no database needed.
4. **Add a second adapter** (e.g., InMemoryUserRepository) and swap it via dependency injection.
5. **Implement event publishing** with a Redis adapter and a fake adapter for tests.
6. **Add an `UpdateUser` use case** that validates email uniqueness and publishes events.
