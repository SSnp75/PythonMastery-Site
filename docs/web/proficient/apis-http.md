---
title: APIs & HTTP
description: REST principles, httpx, authentication, pagination, error handling and API design
---

# APIs & HTTP <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🌐 Web & APIs Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="frameworks/">Web Frameworks</a></span>
  </div>
</div>

---

## Making HTTP requests with httpx

```python
import httpx

# ─── GET ──────────────────────────────────────────
response = httpx.get("https://jsonplaceholder.typicode.com/posts/1")
print(response.status_code)   # 200
print(response.headers["content-type"])   # application/json; charset=utf-8
data = response.json()
print(data["title"])

# ─── POST with JSON ──────────────────────────────
response = httpx.post(
    "https://jsonplaceholder.typicode.com/posts",
    json={"title": "New Post", "body": "Content", "userId": 1},
)
print(response.status_code)   # 201
print(response.json()["id"])  # 101

# ─── PUT (full update) ───────────────────────────
response = httpx.put(
    "https://jsonplaceholder.typicode.com/posts/1",
    json={"title": "Updated", "body": "New body", "userId": 1},
)

# ─── PATCH (partial update) ──────────────────────
response = httpx.patch(
    "https://jsonplaceholder.typicode.com/posts/1",
    json={"title": "Only title changed"},
)

# ─── DELETE ───────────────────────────────────────
response = httpx.delete("https://jsonplaceholder.typicode.com/posts/1")
print(response.status_code)   # 200

# ─── Query parameters ────────────────────────────
response = httpx.get(
    "https://jsonplaceholder.typicode.com/posts",
    params={"userId": 1, "_limit": 5},
)
# URL becomes: .../posts?userId=1&_limit=5

# ─── Custom headers ──────────────────────────────
response = httpx.get(
    "https://api.example.com/data",
    headers={
        "Authorization": "Bearer eyJ...",
        "Accept": "application/json",
        "X-Request-ID": "abc-123",
    },
)

# ─── Timeouts and error handling ──────────────────
try:
    response = httpx.get("https://slow-api.com/data", timeout=5.0)
    response.raise_for_status()   # raises HTTPStatusError for 4xx/5xx
except httpx.TimeoutException:
    print("Request timed out")
except httpx.HTTPStatusError as e:
    print(f"HTTP error: {e.response.status_code}")
except httpx.RequestError as e:
    print(f"Network error: {e}")
```

---

## Async HTTP with httpx

```python
import asyncio
import httpx

async def fetch_all(urls: list[str]) -> list[dict]:
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses if r.status_code == 200]

urls = [f"https://jsonplaceholder.typicode.com/posts/{i}" for i in range(1, 11)]
results = asyncio.run(fetch_all(urls))
print(f"Fetched {len(results)} posts")   # 10 posts in parallel
```

---

## Client sessions (connection reuse)

```python
import httpx

# Reuses TCP connections — much faster for multiple requests
with httpx.Client(
    base_url="https://api.example.com",
    headers={"Authorization": "Bearer token123"},
    timeout=10.0,
) as client:
    users = client.get("/users").json()
    posts = client.get("/posts").json()
    # Same TCP connection reused!
```

---

## REST API design principles

### Resource naming

```
# Good — nouns, plural
GET    /users          → list users
GET    /users/123      → get user 123
POST   /users          → create user
PUT    /users/123      → replace user 123
PATCH  /users/123      → partial update user 123
DELETE /users/123      → delete user 123

# Nested resources
GET    /users/123/posts       → list user 123's posts
POST   /users/123/posts       → create a post for user 123

# Bad — avoid verbs in URLs
GET /getUsers          ✗
POST /createUser       ✗
GET /deleteUser/123    ✗
```

### HTTP status codes

| Code | Meaning | When to use |
|---|---|---|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (include Location header) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error, malformed input |
| 401 | Unauthorized | Missing/invalid authentication |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource, version conflict |
| 422 | Unprocessable Entity | Validation error (FastAPI default) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server failure |

---

## Pagination

### Offset-based (simple)

```python
# Request
GET /users?page=2&per_page=20

# Response
{
    "data": [...],
    "pagination": {
        "page": 2,
        "per_page": 20,
        "total": 156,
        "pages": 8
    }
}
```

### Cursor-based (better for large datasets)

```python
# Request
GET /users?cursor=eyJpZCI6MTAwfQ&limit=20

# Response
{
    "data": [...],
    "next_cursor": "eyJpZCI6MTIwfQ",
    "has_more": true
}
```

Implementation:

```python
import base64, json

def encode_cursor(data: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(data).encode()).decode()

def decode_cursor(cursor: str) -> dict:
    return json.loads(base64.urlsafe_b64decode(cursor).decode())

@app.get("/users")
async def list_users(cursor: str | None = None, limit: int = 20):
    query = db.query(User).order_by(User.id)

    if cursor:
        last = decode_cursor(cursor)
        query = query.filter(User.id > last["id"])

    users = query.limit(limit + 1).all()   # fetch one extra
    has_more = len(users) > limit
    users = users[:limit]

    next_cursor = encode_cursor({"id": users[-1].id}) if has_more else None

    return {
        "data": [u.to_dict() for u in users],
        "next_cursor": next_cursor,
        "has_more": has_more,
    }
```

---

## Authentication patterns

### API Key

```python
# In header
headers = {"X-API-Key": "sk_live_abc123"}

# In query param (less secure — logged in URLs)
GET /data?api_key=sk_live_abc123
```

### JWT (JSON Web Tokens)

```python
import jwt
from datetime import datetime, timedelta

SECRET = "your-secret-key"

def create_token(user_id: int) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

# Usage
token = create_token(user_id=42)
# Client sends: Authorization: Bearer <token>

payload = verify_token(token)
print(payload["sub"])   # 42
```

### OAuth2 flow (simplified)

```python
# 1. Redirect user to provider
# GET https://github.com/login/oauth/authorize?client_id=XXX&scope=user

# 2. User authorizes → redirect back with code
# GET /callback?code=abc123

# 3. Exchange code for token
async def github_callback(code: str):
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            json={"client_id": ID, "client_secret": SECRET, "code": code},
            headers={"Accept": "application/json"},
        )
        access_token = token_response.json()["access_token"]

        # 4. Use token to get user info
        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return user_response.json()
```

---

## Error response format

```python
# Consistent error format
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": [
            {"field": "email", "message": "Not a valid email address"},
            {"field": "age", "message": "Must be >= 0"}
        ]
    }
}

# FastAPI implementation
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"error": {"code": "BAD_REQUEST", "message": str(exc)}},
    )
```

---

## Rate limiting

```python
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        # Remove expired entries
        self.requests[client_id] = [
            t for t in self.requests[client_id] if now - t < self.window
        ]
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        self.requests[client_id].append(now)
        return True

limiter = RateLimiter(max_requests=100, window_seconds=60)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    if not limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded. Try again later."},
            headers={"Retry-After": "60"},
        )
    return await call_next(request)
```

---

## API Versioning

```python
# URL versioning (most common)
# /api/v1/users
# /api/v2/users

from fastapi import APIRouter

v1_router = APIRouter(prefix="/api/v1")
v2_router = APIRouter(prefix="/api/v2")

@v1_router.get("/users")
async def get_users_v1():
    return [{"name": "Alice"}]

@v2_router.get("/users")
async def get_users_v2():
    return [{"first_name": "Alice", "last_name": "Smith"}]

app.include_router(v1_router)
app.include_router(v2_router)
```

---

## Practice Exercises

1. **Build a typed API client** class for a public API (GitHub, OpenWeather, etc.) with error handling and retries.
2. **Implement cursor-based pagination** in a FastAPI endpoint backed by SQLite.
3. **Implement JWT authentication** with registration, login, refresh tokens and protected routes.
4. **Build a rate limiter** using Redis (sliding window algorithm).
5. **Design a RESTful API** for an e-commerce platform (products, orders, users, reviews) — write the OpenAPI spec first.
6. **Write comprehensive tests** for every HTTP method, status code and error case.
