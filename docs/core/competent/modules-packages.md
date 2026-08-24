---
title: Modules & Packages
description: Organising Python code into modules, packages and namespaces
---

# Modules & Packages <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisite: <a href="../beginner/functions/">Functions</a></span>
  </div>
</div>

---

## Modules

A module is just a `.py` file. Import it by name.

```python
# math_utils.py
def add(a, b):
    return a + b

PI = 3.14159
```

```python
# main.py
import math_utils
print(math_utils.add(2, 3))

from math_utils import add, PI
print(add(2, 3))

from math_utils import add as addition   # alias
```

---

## Packages

A package is a folder with an `__init__.py` file.

```
myproject/
├── __init__.py
├── core/
│   ├── __init__.py
│   └── engine.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

```python
from myproject.core.engine import start
from myproject.utils.helpers import format_name
```

---

## `__init__.py`

```python
# myproject/__init__.py
from .core.engine import start
from .utils.helpers import format_name

__all__ = ["start", "format_name"]   # controls "from myproject import *"
```

---

## The `if __name__ == "__main__"` guard

```python
def main():
    print("Running as script!")

if __name__ == "__main__":
    main()
```

This ensures code runs only when the file is executed directly, not when imported.

---

## Practice exercises

1. Split a single-file program into 3 modules and import between them.
2. Create a package with `__init__.py` that exposes a clean public API.
3. Write a module that works both as an importable library and a CLI script.
