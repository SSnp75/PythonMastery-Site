---
title: CI/CD Pipelines
description: GitHub Actions, automated testing, deployment and release workflows
---

# CI/CD Pipelines <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🚀 Deployment · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
  </div>
</div>

---

## GitHub Actions — complete pipeline

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: pip install -e ".[test]"

      - name: Lint
        run: ruff check .

      - name: Type check
        run: mypy src/

      - name: Test
        run: pytest --cov=src --cov-report=xml
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test_db

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker tag myapp:${{ github.sha }} myregistry/myapp:latest
          docker push myregistry/myapp:latest

      - name: Deploy
        run: |
          ssh deploy@production "docker pull myregistry/myapp:latest && docker-compose up -d"
```

---

## Practice Exercises

1. **Set up CI** — lint, type check, test on every push with 3 Python versions.
2. **Add deployment** — auto-deploy to a server on merge to main.
3. **Add caching** — cache pip dependencies between runs for faster builds.
4. **Matrix testing** — test against multiple OS + Python version combinations.
5. **Add release workflow** — build wheel, publish to PyPI on git tag.
