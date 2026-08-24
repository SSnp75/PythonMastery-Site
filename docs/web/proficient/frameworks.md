---
title: Web Frameworks
description: Flask, FastAPI and Django — building production web applications in Python
---

# Web Frameworks <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🌐 Web & APIs Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 weeks</span>
    <span>📚 Prerequisites: <a href="../../core/intermediate/decorators/">Decorators</a>, <a href="../../core/intermediate/typing/">Type Hints</a></span>
  </div>
</div>

---

## FastAPI (recommended for modern APIs)

### Basic application

```python
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

app = FastAPI(title="My API", version="1.0.0")

# ─── Models ───────────────────────────────────────
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    description: Optional[str] = None
    in_stock: bool = True

class ItemResponse(ItemCreate):
    id: int

# ─── In-memory store ──────────────────────────────
items_db: dict[int, ItemResponse] = {}
next_id = 1

# ─── Routes ───────────────────────────────────────
@app.get("/")
async def root():
    return {"message": "API is running", "items_count": len(items_db)}

@app.post("/items/", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate):
    global next_id
    new_item = ItemResponse(id=next_id, **item.model_dump())
    items_db[next_id] = new_item
    next_id += 1
    return new_item

@app.get("/items/", response_model=list[ItemResponse])
async def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    in_stock: Optional[bool] = None,
):
    results = list(items_db.values())
    if in_stock is not None:
        results = [i for i in results if i.in_stock == in_stock]
    return results[skip : skip + limit]

@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]

@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item: ItemCreate):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    updated = ItemResponse(id=item_id, **item.model_dump())
    items_db[item_id] = updated
    return updated

@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

```bash
# Run:
uvicorn main:app --reload

# Auto-generated docs available at:
# http://127.0.0.1:8000/docs      (Swagger UI)
# http://127.0.0.1:8000/redoc     (ReDoc)
```

### Dependency Injection

```python
from fastapi import Depends, Header, HTTPException

# Database session dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth dependency
async def get_current_user(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

# Use in routes
@app.get("/profile")
async def profile(user = Depends(get_current_user), db = Depends(get_db)):
    return db.query(User).filter_by(id=user.id).first()
```

### Middleware

```python
import time
from fastapi import Request

@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{elapsed:.4f}"
    return response
```

### Background Tasks

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # Slow operation — runs in background
    import time
    time.sleep(2)
    print(f"Email sent to {email}")

@app.post("/notify/")
async def notify(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email, "Welcome!")
    return {"message": "Notification queued"}
```

---

## Flask (lightweight, flexible)

### Basic application

```python
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

items = []

@app.route("/")
def index():
    return jsonify({"status": "ok", "items": len(items)})

@app.route("/items", methods=["GET"])
def get_items():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    start = (page - 1) * per_page
    return jsonify(items[start:start + per_page])

@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json()
    if not data or "name" not in data:
        abort(400, description="Name is required")
    item = {"id": len(items) + 1, **data}
    items.append(item)
    return jsonify(item), 201

@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = next((i for i in items if i["id"] == item_id), None)
    if not item:
        abort(404, description="Item not found")
    return jsonify(item)

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": str(error.description)}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": str(error.description)}), 400

if __name__ == "__main__":
    app.run(debug=True)
```

### Flask Blueprints (modular structure)

```python
# users/routes.py
from flask import Blueprint, jsonify

users_bp = Blueprint("users", __name__, url_prefix="/users")

@users_bp.route("/")
def list_users():
    return jsonify([])

@users_bp.route("/<int:user_id>")
def get_user(user_id):
    return jsonify({"id": user_id})

# app.py
from flask import Flask
from users.routes import users_bp

app = Flask(__name__)
app.register_blueprint(users_bp)
```

### Flask with SQLAlchemy

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), unique=True)

with app.app_context():
    db.create_all()
```

---

## Django (full-featured framework)

### Project structure

```
myproject/
├── manage.py
├── myproject/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── myapp/
    ├── models.py
    ├── views.py
    ├── serializers.py
    ├── urls.py
    └── tests.py
```

### Django REST Framework — API views

```python
# models.py
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

# serializers.py
from rest_framework import serializers

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = "__all__"

# views.py
from rest_framework import viewsets
from .models import Article
from .serializers import ArticleSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filterset_fields = ["published"]
    search_fields = ["title", "content"]

# urls.py
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register("articles", ArticleViewSet)
urlpatterns = router.urls
```

---

## Framework comparison

| Feature | FastAPI | Flask | Django |
|---|---|---|---|
| **Speed** | Very fast (async, Starlette) | Good | Good |
| **Type safety** | Built-in (Pydantic) | Manual | Manual (DRF serializers) |
| **Auto-docs** | Yes (OpenAPI/Swagger) | No (use flasgger) | Yes (DRF browsable API) |
| **ORM** | No (bring your own) | No (use Flask-SQLAlchemy) | Yes (built-in) |
| **Admin panel** | No | No | Yes (built-in) |
| **Auth** | Manual (fastapi-users) | Manual (Flask-Login) | Built-in |
| **Async** | Native | Extension (quart) | Partial (Django 4.1+) |
| **Learning curve** | Medium | Low | High |
| **Best for** | APIs, microservices | Simple apps, prototypes | Full web apps, CMS |
| **When to choose** | Modern REST/GraphQL APIs | Quick scripts, small APIs | Large apps with admin |

---

## Deployment patterns

```python
# FastAPI with Gunicorn + Uvicorn workers
# gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Flask with Gunicorn
# gunicorn app:app -w 4 --bind 0.0.0.0:5000

# Django with Gunicorn
# gunicorn myproject.wsgi:application -w 4 --bind 0.0.0.0:8000
```

### Docker deployment

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Testing web applications

```python
# FastAPI testing
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_item():
    response = client.post("/items/", json={"name": "Widget", "price": 9.99})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Widget"
    assert "id" in data

def test_get_nonexistent():
    response = client.get("/items/9999")
    assert response.status_code == 404

# Flask testing
def test_flask_app():
    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200
```

---

## Practice Exercises

1. **Build a complete CRUD API** with FastAPI — User model with registration, login (JWT), profile CRUD.
2. **Build the same API in Flask** and compare the code volume and structure.
3. **Add pagination, filtering, and sorting** to a list endpoint.
4. **Implement rate limiting** middleware that blocks after N requests per minute.
5. **Write integration tests** for all endpoints using TestClient.
6. **Dockerize the application** and deploy with docker-compose (app + PostgreSQL + Redis).
