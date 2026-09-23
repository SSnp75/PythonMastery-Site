---
title: "Tools"
description: The Python toolbox — editors, linters, formatters, type checkers, profilers and CI
---

# Tools <span class="pm-badge pm-badge-beginner">Reference</span>

<div class="pm-topic-header">
  <strong>📚 Reference</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Quick reference</span>
    <span>📚 The modern Python toolbox</span>
  </div>
</div>

---

A practical map of the tools that make Python development productive. Where the field has a clear modern default, it's noted.

---

## Editors & IDEs

| Tool | Notes |
|---|---|
| **VS Code** | Free, huge extension ecosystem, the Python extension + Pylance is excellent. The common default. |
| **PyCharm** | Full IDE, deep refactoring and debugging, great for large projects. Free Community edition. |
| **Neovim / Vim** | Lightweight, keyboard-driven; with LSP plugins it rivals IDEs. |
| **Jupyter** | Notebooks for data science and exploration, not app development. |

---

## Package & environment management

| Tool | What it does | Notes |
|---|---|---|
| **uv** | Installs packages, manages venvs, resolves deps — very fast | The rising modern default (Rust-based). |
| **pip + venv** | The built-in baseline | Always available; slower resolution. |
| **Poetry** | Dependency management + packaging | Popular, `pyproject.toml`-based. |
| **conda** | Env + package manager for scientific stacks | Handles non-Python deps (C libs). |

```bash
# uv — create env + install, fast
uv venv
uv pip install requests

# pip + venv — the built-in way
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install requests
```

**Recommendation:** try **uv** for new projects — it's dramatically faster and consolidates several tools. `pip + venv` is the always-there fallback.

---

## Linters & formatters

| Tool | Role | Notes |
|---|---|---|
| **ruff** | Linter **and** formatter | Extremely fast (Rust); replaces flake8 + isort + more. The modern default. |
| **black** | Opinionated formatter | Zero-config; ruff's formatter is black-compatible. |
| **flake8** | Classic linter | Being superseded by ruff. |
| **pylint** | Deep linter | Thorough but slower/noisier. |

```bash
ruff check .        # lint
ruff format .       # format
```

**Recommendation:** **ruff** for both linting and formatting — one fast tool instead of several. See [Static Analysis Engines](../research/static-analysis-engines.md) for how these work under the hood.

---

## Type checkers

| Tool | Notes |
|---|---|
| **mypy** | The original, widely used static type checker. |
| **pyright** | Fast, powers VS Code's Pylance; great inference. |
| **ty / pyrefly** | Newer fast checkers (emerging). |

```bash
mypy src/
```

Type checking catches a whole class of bugs before runtime. See [Typing & Type Hints](../core/intermediate/typing.md).

---

## Testing

| Tool | Role |
|---|---|
| **pytest** | The de-facto test framework — fixtures, parametrization, plugins. |
| **coverage.py** | Measures which lines your tests execute. |
| **hypothesis** | Property-based testing (generates test cases). |
| **tox / nox** | Run tests across multiple Python versions. |

```bash
pytest -v
pytest --cov=src
```

See the Testing section for depth.

---

## Debuggers & profilers

| Tool | Role |
|---|---|
| **pdb / breakpoint()** | Built-in interactive debugger (`breakpoint()` drops you in). |
| **cProfile** | Built-in function-level profiler. |
| **py-spy** | Sampling profiler that attaches to a running process (no code change). |
| **line_profiler** | Line-by-line timing. |
| **memray / tracemalloc** | Memory profiling. |

```python
breakpoint()          # pause here and inspect interactively
```

See [Profiling](../systems/advanced/profiling.md) and [Debugging](../core/competent/debugging.md).

---

## CI/CD

| Tool | Notes |
|---|---|
| **GitHub Actions** | CI/CD integrated with GitHub; free for public repos. |
| **pre-commit** | Runs linters/formatters automatically before each commit. |
| **GitLab CI / CircleCI** | Alternatives. |

A `pre-commit` config that runs ruff on every commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
      - id: ruff-format
```

See the Deployment section's CI/CD topic.

---

## A recommended modern starter stack

For a new project in 2026, a clean, fast setup:

- **Environment/packages:** uv
- **Lint + format:** ruff
- **Type check:** mypy or pyright
- **Test:** pytest (+ coverage)
- **Editor:** VS Code + Pylance
- **CI:** GitHub Actions + pre-commit

This gives you speed, correctness checks, and automation with minimal configuration.

---

## Related

- [Templates](templates.md) — project layout and configs
- [Python Packaging](../web/competent/packaging.md)
- [Code Snippets](code-snippets.md)
