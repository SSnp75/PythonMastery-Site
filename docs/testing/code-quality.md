---
title: Code Quality Tools
description: ruff, mypy, black, isort, pre-commit hooks and enforcing standards
---

# Code Quality Tools <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🧪 Testing Track · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 days</span>
  </div>
</div>

---

## The modern Python quality stack

| Tool | Purpose | Speed |
|---|---|---|
| **ruff** | Linter + formatter (replaces flake8, isort, black) | Extremely fast |
| **mypy** | Static type checker | Moderate |
| **black** | Opinionated code formatter | Fast |
| **isort** | Import sorter | Fast |
| **bandit** | Security linter | Fast |
| **pre-commit** | Git hooks to run tools automatically | — |

---

## ruff — the all-in-one tool

```bash
pip install ruff

# Lint (find issues)
ruff check .
ruff check --fix .    # auto-fix what's possible

# Format (replace black + isort)
ruff format .
ruff format --check .   # check only, don't modify
```

Configuration:
```toml
# pyproject.toml
[tool.ruff]
target-version = "py313"
line-length = 100

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
    "SIM",  # flake8-simplify
    "TCH",  # type-checking imports
    "RUF",  # ruff-specific rules
]
ignore = ["E501"]   # line too long (handled by formatter)

[tool.ruff.lint.isort]
known-first-party = ["mypackage"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### Common ruff fixes:

```python
# Before ruff
from typing import List, Dict, Optional
import os
import sys
from pathlib import Path

x = dict()
y = list()
if type(x) == dict:
    pass

# After ruff --fix
import os
import sys
from pathlib import Path

x = {}
y = []
if isinstance(x, dict):
    pass
# typing imports removed (use built-in types in 3.9+)
# imports sorted
# dict()/list() → {}/[]
# type() == → isinstance()
```

---

## mypy — static type checking

```bash
pip install mypy
mypy src/
mypy --strict src/   # stricter checks
```

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

Common errors and fixes:
```python
# Error: Function is missing a return type annotation
def process(data):  # ← add -> ReturnType
    ...

# Fix:
def process(data: list[dict]) -> list[str]:
    ...

# Error: Incompatible return value type (got "Optional[str]", expected "str")
def get_name(user) -> str:
    return user.get("name")   # might be None!

# Fix:
def get_name(user) -> str:
    return user.get("name", "Unknown")
```

---

## pre-commit — automate on every commit

```bash
pip install pre-commit
```

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
```

```bash
pre-commit install         # set up git hooks
pre-commit run --all-files # run on everything now
# After this, tools run automatically on every git commit
```

---

## CI integration

```yaml
# .github/workflows/quality.yml
name: Quality
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.13" }
      - run: pip install ruff mypy
      - run: ruff check .
      - run: ruff format --check .
      - run: mypy src/
```

---

## Practice Exercises

1. **Set up ruff** on an existing project and fix all reported issues.
2. **Add mypy** with `--strict` and fix all type errors.
3. **Configure pre-commit** with ruff + mypy and verify it blocks bad commits.
4. **Create a CI pipeline** that runs lint, format check, type check and tests.
5. **Write a custom ruff rule** using `pyproject.toml` configuration.
