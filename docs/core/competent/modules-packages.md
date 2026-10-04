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

!!! info "When you'd use this"
    Organising Python code into modules, packages and namespaces.

    Organize a growing codebase: split a long script into modules, group modules into packages, and expose a clean public API with `__init__.py` and `__all__`.


## Modules

*A single `.py` file of reusable code you `import` elsewhere. Use modules to split a growing script into focused, testable units.*

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

*A directory of modules (with `__init__.py`) that groups related code under one namespace. Use packages to organize a library or app into subsystems.*

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

*Runs when the package is imported — use it to expose a clean public API and set `__all__` so `from pkg import *` only pulls intended names.*

```python
# myproject/__init__.py
from .core.engine import start
from .utils.helpers import format_name

__all__ = ["start", "format_name"]   # controls "from myproject import *"
```

---

## The `if __name__ == "__main__"` guard

*Make a file work both as an importable module and a runnable script — the guarded code runs only on direct execution, not on import.*

```python
def main():
    print("Running as script!")

if __name__ == "__main__":
    main()
```

This ensures code runs only when the file is executed directly, not when imported.

---

## Import forms, compared

```python
import math                      # math.sqrt(4)
from math import sqrt            # sqrt(4)
from math import sqrt as sr      # sr(4)
from math import *               # pulls public names (avoid in libraries)
```

```python
import math
print(math.sqrt(16))   # 4.0

from math import pi
print(round(pi, 2))    # 3.14
```

---

## Relative vs absolute imports

Inside a package, relative imports use leading dots:

```python
# absolute (preferred for clarity)
from myproject.utils.helpers import format_name

# relative (within the same package)
from .helpers import format_name      # same package
from ..core.engine import start       # parent package
```

Relative imports only work inside a package (a module run as a script can't use them).

---

## What `import` actually does

The first import executes the module top to bottom and caches it in `sys.modules`;
later imports reuse the cached module (the body does **not** re-run):

```python
import sys
import json              # importing a second time...
import json              # ...reuses the cached module object
print("json" in sys.modules)   # True
```

---

## Inspecting a module

```python
import math

print(math.__name__)                                   # math
print("sqrt" in dir(math))                             # True
print(type(math).__name__)                             # module
```

---

## Namespace packages (no `__init__.py`)

Since PEP 420, a directory without `__init__.py` can still be an importable namespace
package, letting one logical package span multiple directories. Prefer a regular package
(with `__init__.py`) unless you specifically need this.

---

## Practice exercises

1. Split a single-file program into 3 modules and import between them.
2. Create a package with `__init__.py` that exposes a clean public API.
3. Write a module that works both as an importable library and a CLI script.
