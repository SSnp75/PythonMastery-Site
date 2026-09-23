---
title: "Templates"
description: Reusable starting points — project layout, notes, experiment logs and ADRs
---

# Templates <span class="pm-badge pm-badge-beginner">Reference</span>

<div class="pm-topic-header">
  <strong>📚 Reference</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Quick reference</span>
    <span>📚 Copy and adapt</span>
  </div>
</div>

---

Reusable starting points so you don't reinvent structure every time. Copy, adapt, keep what helps.

---

## Modern Python project layout

The current standard uses `pyproject.toml` and a `src/` layout:

```
myproject/
├── pyproject.toml          # single source of config (build, deps, tools)
├── README.md
├── src/
│   └── myproject/
│       ├── __init__.py
│       └── core.py
├── tests/
│   └── test_core.py
└── .gitignore
```

A minimal `pyproject.toml`:

```toml
[project]
name = "myproject"
version = "0.1.0"
description = "A short description"
requires-python = ">=3.11"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 88
```

**Why `src/` layout:** it prevents accidentally importing your package from the working directory instead of the installed version, which catches packaging bugs early. See [Python Packaging](../web/competent/packaging.md).

---

## Test file template (pytest)

```python
import pytest
from myproject.core import my_function

def test_happy_path():
    assert my_function(2) == 4

def test_edge_case():
    assert my_function(0) == 0

def test_raises_on_bad_input():
    with pytest.raises(ValueError):
        my_function(-1)

@pytest.mark.parametrize("inp,expected", [(1, 2), (2, 4), (3, 6)])
def test_multiple_cases(inp, expected):
    assert my_function(inp) == expected
```

See the Testing section for depth on fixtures, mocking, and parametrization.

---

## Architecture Decision Record (ADR)

A short doc capturing *why* a significant decision was made. Store these in `docs/adr/NNNN-title.md`. Template:

```markdown
# ADR 0001: Use PostgreSQL for primary storage

## Status
Accepted — 2026-01-15

## Context
We need a primary datastore. Data is relational, we need
transactions and complex queries, and the team knows SQL.

## Decision
Use PostgreSQL as the primary database.

## Alternatives considered
- MongoDB — rejected: our data is strongly relational.
- SQLite — rejected: won't handle our concurrency needs.

## Consequences
- Gain: strong consistency, mature tooling, rich queries.
- Cost: must run and operate a Postgres server.
```

**Why ADRs matter:** two years later, nobody remembers *why* a choice was made. An ADR prevents re-litigating settled decisions and stops someone "fixing" something that was deliberate. See [Long-term Codebase Evolution](../web/expert/codebase-evolution.md).

---

## Experiment log (for research/data work)

```markdown
# Experiment: <name>   —   <date>

## Hypothesis
What you expect to happen and why.

## Setup
- Data / inputs:
- Parameters:
- Environment / versions:

## Result
- What actually happened (metrics, output).

## Conclusion
- Confirmed / rejected? Next step?
```

Keeping a dated log turns scattered trial-and-error into a traceable record — invaluable for data science and any experimental work.

---

## Daily note / learning log

```markdown
# <date>

## Learned
- 

## Built / did
- 

## Blocked on
- 

## Tomorrow
- 
```

A lightweight habit that compounds — a searchable history of what you learned and did.

---

## `.gitignore` starter (Python)

```gitignore
__pycache__/
*.py[cod]
.venv/
venv/
*.egg-info/
dist/
build/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.env
.DS_Store
```

---

## Related

- [Python Packaging](../web/competent/packaging.md) — publishing projects
- [Tools](tools.md) — editors, linters, formatters
- [Code Snippets](code-snippets.md) — reusable code
