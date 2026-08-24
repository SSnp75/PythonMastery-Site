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

## Virtual environments

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

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

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

## Publishing to PyPI

```bash
pip install build twine
python -m build
twine upload dist/*
```

---

## Practice exercises

1. Create a project with `pyproject.toml` and install it in editable mode (`pip install -e .`).
2. Add a CLI entry point that works after install.
3. Publish a test package to test.pypi.org.
