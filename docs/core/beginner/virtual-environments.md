---
title: Virtual Environments
description: Isolate project dependencies with venv, pip and requirements files
---

# Virtual Environments <span class="pm-badge pm-badge-beginner">Beginner</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 1</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 day</span>
    <span>📚 Prerequisite: <a href="python-basics/">Python Basics</a></span>
  </div>
</div>

---

!!! info "When you'd use this"
    Isolate each project's dependencies so they never collide.

    Create a per-project sandbox for installed packages — so Project A can use an old library version and Project B a new one, without either breaking the other or your system Python.


## Why virtual environments exist

*Without isolation, every `pip install` dumps packages into one shared location, so two projects that need different versions of the same library can't coexist.*

Imagine you have two projects. One needs `requests` version 2.25, the other needs 2.31. If you install packages globally, the second install overwrites the first — and now one project is quietly broken. Multiply that across dozens of projects and you get "dependency hell."

A **virtual environment** is a self-contained folder holding its own Python interpreter link and its own `site-packages` directory. When it's active, `pip install` puts packages *there*, not system-wide. Each project gets its own clean, isolated set of dependencies.

!!! warning "Don't install into system Python"
    On many systems, `pip install` without an active environment either needs admin rights or can break OS tools that rely on specific package versions. Modern Python (3.11+) will often refuse with an "externally-managed-environment" error. A virtual environment is the correct fix — not `--break-system-packages`.

---

## Creating and activating a venv

*`venv` ships with Python — no install needed. Create once per project, then activate it in each new terminal session.*

Python's built-in `venv` module is all you need to start.

```bash
# Create a virtual environment named ".venv" in your project folder
python -m venv .venv
```

Activating it differs by operating system:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (cmd.exe)
.venv\Scripts\activate.bat
```

Once active, your shell prompt is prefixed with the environment name:

```text
(.venv) $ python --version
Python 3.12.3
```

That `(.venv)` prefix is your signal that installs and runs now happen inside the sandbox. To leave it:

```bash
deactivate
```

!!! note "Why name it `.venv`?"
    The leading dot keeps it hidden in listings, and `.venv` is the convention most editors (including VS Code) auto-detect. Add it to `.gitignore` — you never commit the environment itself, only the list of what to install (see below).

---

## Installing packages with pip

*With the environment active, `pip` installs into it. Check what's installed with `pip list`.*

```bash
# Install a package (goes into the active venv only)
pip install requests

# Install a specific version
pip install "requests==2.31.0"

# See what's installed
pip list

# Upgrade pip itself
python -m pip install --upgrade pip
```

A quick sanity check that isolation is working — run this inside an active venv:

```python
import sys

# Inside an active venv, this points into your project's .venv folder,
# not the system Python installation.
print(sys.prefix)
```

Example output (macOS/Linux):

```text
/home/you/myproject/.venv
```

The path points into your project, confirming packages land in the sandbox rather than system-wide.

---

## requirements.txt: sharing dependencies

*Pin your project's dependencies to a text file so anyone (including future you, or CI) can recreate the exact environment.*

You don't commit the `.venv` folder — you commit a list of what it should contain.

```bash
# Freeze the current environment to a file
pip freeze > requirements.txt
```

That produces a pinned list:

```text
certifi==2024.2.2
charset-normalizer==3.3.2
idna==3.6
requests==2.31.0
urllib3==2.2.1
```

Anyone cloning your project then recreates the environment in two steps:

```bash
python -m venv .venv
source .venv/bin/activate        # or the Windows equivalent
pip install -r requirements.txt
```

!!! tip "Keep a readable top-level list too"
    `pip freeze` captures *everything*, including sub-dependencies. Many projects also keep a short, human-edited `requirements.txt` listing only the packages they directly use (e.g. just `requests` and `flask`), and let pip resolve the rest. For reproducible deployments, the fully pinned version is safer.

---

## Modern alternatives

*`venv` + `pip` is the baseline every Python developer should know. Several tools wrap or replace it with extra convenience — worth knowing by name.*

| Tool | What it adds | When to reach for it |
|---|---|---|
| **`venv` + `pip`** | Nothing extra — the standard-library baseline | Always a safe default; zero to install |
| **`uv`** | Extremely fast installs; creates venvs and resolves deps in one tool | Modern projects wanting speed |
| **`poetry`** | Dependency resolution + lock file + packaging in one | Libraries you'll publish, or teams wanting reproducible locks |
| **`pipenv`** | Combines pip + virtualenv with a `Pipfile` lock | Projects already standardized on it |
| **`conda`** | Manages non-Python deps too (C libs, CUDA) | Data science / scientific stacks |

Start with `venv` + `pip` until the workflow is second nature. The alternatives solve real problems (speed, lock files, native dependencies), but they all build on the same core idea you just learned: an isolated, per-project set of packages.

---

## Practice exercises

1. Create a new project folder, make a `.venv` inside it, activate it, and confirm `sys.prefix` points into that folder.
2. Install `requests` in the environment, run `pip freeze > requirements.txt`, then deactivate and inspect the file.
3. Delete the `.venv` folder entirely, recreate it, and restore your packages from `requirements.txt` in one command.
4. Add a `.gitignore` line that excludes `.venv/` but keeps `requirements.txt` tracked, and explain in a comment why you commit one but not the other.
5. Research the "externally-managed-environment" error: what causes it, and why is creating a venv the right fix rather than forcing a system install?
