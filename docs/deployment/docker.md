---
title: Docker & Compose
description: Dockerfiles, multi-stage builds, docker-compose and container best practices
---

# Docker & Compose <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🚀 Deployment · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
  </div>
</div>

---

## Dockerfile for Python apps

```dockerfile
# ─── Multi-stage build (smaller final image) ─────
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY src/ ./src/
COPY pyproject.toml .

# Non-root user (security best practice)
RUN useradd -m appuser
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## docker-compose (local dev environment)

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://postgres:secret@db:5432/myapp
      REDIS_URL: redis://cache:6379
    depends_on:
      db: { condition: service_healthy }
      cache: { condition: service_started }
    volumes:
      - ./src:/app/src   # hot reload in dev

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: myapp
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

  cache:
    image: redis:7-alpine
    ports: ["6379:6379"]

volumes:
  pgdata:
```

```bash
docker compose up -d        # start all services
docker compose logs -f app  # follow app logs
docker compose down         # stop and remove
docker compose exec app bash  # shell into container
```

---

## Best practices

!!! tip "Docker for Python"
    - Use `python:3.13-slim` (not full image — 5x smaller)
    - Use multi-stage builds (separate build deps from runtime)
    - Pin dependency versions (reproducible builds)
    - Run as non-root user
    - Add `.dockerignore` (exclude `.git`, `__pycache__`, `.venv`, `tests/`)
    - Use `HEALTHCHECK` for orchestrators to monitor

---

## Practice Exercises

1. **Dockerize a FastAPI app** with multi-stage build, non-root user and health check.
2. **Create docker-compose** for app + PostgreSQL + Redis with proper health checks.
3. **Optimize image size** — compare full vs slim vs alpine, measure with `docker images`.
4. **Add hot reload** for development using volume mounts.
5. **Build a CI pipeline** that builds Docker image and pushes to Docker Hub.
