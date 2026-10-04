---
title: Python Packaging
description: pip, venv, pyproject.toml and distributing your code
---

# Python Packaging <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🌐 Web & APIs Track · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
  </div>
</div>

---

!!! info "When you'd use this"
    pip, venv, pyproject.toml and distributing your code.

    Package and distribute code: set up `pyproject.toml`, manage dependencies with venv/uv, and publish a library or CLI to PyPI.


## Virtual environments

*Isolate a project's dependencies from the system Python so projects don't conflict — always work inside one.*

```bash
# Create
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install packages
pip install requests flask

# Freeze dependencies
pip freeze > requirements.txt

# Install from file
pip install -r requirements.txt
```

---

## pyproject.toml (modern standard)

*The single config file declaring your project's metadata, dependencies, and build system.*

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "mypackage"
version = "0.1.0"
description = "My awesome package"
requires-python = ">=3.10"
dependencies = [
    "requests>=2.28",
    "click>=8.0",
]

[project.scripts]
mycommand = "mypackage.cli:main"
```

---

## Project structure

*The conventional `src/` layout that keeps imports honest and tests separate.*

```
mypackage/
├── pyproject.toml
├── README.md
├── src/
│   └── mypackage/
│       ├── __init__.py
│       └── core.py
└── tests/
    └── test_core.py
```

---

## uv — the fast modern workflow

*uv — the fast modern workflow, part of Python Packaging.*

[`uv`](https://docs.astral.sh/uv/) is a fast, all-in-one package and project manager that
replaces most `pip` + `venv` + `pip-tools` workflows:

```bash
uv init myproject          # scaffold a project with pyproject.toml
uv add requests            # add a dependency and update the lockfile
uv add --dev pytest ruff   # add dev dependencies
uv run pytest              # run inside the managed environment
uv sync                    # install exactly what the lockfile pins
uv lock                    # regenerate uv.lock
```

`uv` creates and manages the virtual environment for you, and `uv.lock` gives reproducible
installs across machines.

---

## Publishing to PyPI

*Build a wheel and upload it so others can `pip install` your package.*

```bash
pip install build twine
python -m build            # produces dist/*.whl and dist/*.tar.gz
twine upload dist/*        # upload to PyPI (use test.pypi.org first)
```

With `uv` you can instead run `uv build` and `uv publish`.

---

## Practice exercises

1. Create a project with `pyproject.toml` and install it in editable mode (`pip install -e .`).
2. Add a CLI entry point that works after install.
3. Publish a test package to test.pypi.org.
