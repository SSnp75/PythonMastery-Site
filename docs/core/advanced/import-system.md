---
title: Import System Internals
description: importlib, finders, loaders, import hooks, sys.path and lazy imports
---

# Import System Internals <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 5</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisite: <a href="../competent/modules-packages/">Modules & Packages</a></span>
  </div>
</div>

---

## How `import` works — the full process

When Python executes `import mymodule`, this happens:

```python
# Pseudocode of the import machinery
def import_module(name):
    # 1. Check the cache
    if name in sys.modules:
        return sys.modules[name]

    # 2. Find the module using finders
    spec = None
    for finder in sys.meta_path:
        spec = finder.find_spec(name, path=None)
        if spec is not None:
            break

    if spec is None:
        raise ModuleNotFoundError(f"No module named '{name}'")

    # 3. Create the module object
    module = spec.loader.create_module(spec)
    if module is None:
        module = types.ModuleType(name)

    # 4. Register in cache BEFORE executing (handles circular imports)
    sys.modules[name] = module

    # 5. Execute the module code
    spec.loader.exec_module(module)

    return module
```

---

## sys.meta_path — the finder chain

```python
import sys

for finder in sys.meta_path:
    print(type(finder).__name__)

# Output (typical):
# BuiltinImporter       — finds built-in modules (sys, os, etc.)
# FrozenImporter        — finds frozen modules
# PathFinder            — finds modules on sys.path (the most common)
```

---

## sys.path — where PathFinder searches

```python
import sys

for p in sys.path:
    print(p)

# Output:
# '' (current directory)
# /usr/lib/python313.zip
# /usr/lib/python3.13
# /usr/lib/python3.13/lib-dynload
# /home/user/.local/lib/python3.13/site-packages
# /usr/lib/python3.13/site-packages
```

### Modifying sys.path at runtime:

```python
import sys
sys.path.insert(0, "/my/custom/path")

# Now Python will search /my/custom/path first
```

---

## Writing a custom Finder

```python
import importlib.abc
import importlib.util
import sys
import types

class UppercaseImporter(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """
    Custom importer that intercepts imports starting with 'upper_'
    and provides a module with an uppercase version of the name.
    """

    def find_spec(self, name, path, target=None):
        if name.startswith("upper_"):
            return importlib.util.spec_from_loader(name, self)
        return None

    def create_module(self, spec):
        return None   # use default module creation

    def exec_module(self, module):
        # Module that provides the uppercase name
        real_name = module.__name__[6:]   # remove 'upper_' prefix
        module.value = real_name.upper()
        module.greet = lambda: f"Hello from {module.value}!"


# Install the importer
sys.meta_path.insert(0, UppercaseImporter())

# Now this works:
import upper_world
print(upper_world.value)     # WORLD
print(upper_world.greet())   # Hello from WORLD!

import upper_python
print(upper_python.value)    # PYTHON
```

---

## Writing a custom Loader

```python
import importlib.abc
import importlib.util
import sys

class DatabaseLoader(importlib.abc.Loader):
    """Load module source code from a database."""

    def __init__(self, db_connection):
        self.db = db_connection

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        # Fetch source from database
        source = self.db.get_source(module.__name__)
        code = compile(source, f"<db:{module.__name__}>", "exec")
        exec(code, module.__dict__)


class DatabaseFinder(importlib.abc.MetaPathFinder):
    def __init__(self, db_connection):
        self.loader = DatabaseLoader(db_connection)
        self.db = db_connection

    def find_spec(self, name, path, target=None):
        if self.db.has_module(name):
            return importlib.util.spec_from_loader(name, self.loader)
        return None
```

---

## Import hooks — modifying imports globally

```python
import sys
import importlib

class ImportLogger:
    """Log every import."""

    def find_module(self, name, path=None):
        print(f"  📦 Importing: {name}")
        return None   # return None = "I don't handle this, let others try"

sys.meta_path.insert(0, ImportLogger())

import json       # prints: 📦 Importing: json
import hashlib    # prints: 📦 Importing: hashlib
```

---

## Lazy imports (deferred loading)

```python
import importlib
import types

class LazyModule(types.ModuleType):
    """Module that delays actual import until first attribute access."""

    def __init__(self, name):
        super().__init__(name)
        self._loaded = False

    def _load(self):
        if not self._loaded:
            self._loaded = True
            # Actually import and copy attributes
            real_module = importlib.import_module(self.__name__)
            self.__dict__.update(real_module.__dict__)

    def __getattr__(self, name):
        self._load()
        return self.__dict__[name]


def lazy_import(name):
    """Return a lazy module that loads on first access."""
    module = LazyModule(name)
    sys.modules[name] = module
    return module


# Usage: numpy won't be loaded until you access an attribute
np = lazy_import("numpy")
# ... much later ...
# array = np.array([1, 2, 3])   # NOW numpy loads
```

---

## Circular imports — how Python handles them

```python
# a.py
import b
x = 10
print(f"a.py: b.y = {b.y}")

# b.py
import a
y = 20
print(f"b.py: a.x = {a.x}")
```

What happens when you `import a`:

1. Python starts executing `a.py`
2. `a.py` hits `import b`
3. Python starts executing `b.py`
4. `b.py` hits `import a`
5. `a` is already in `sys.modules` (partial!) → returns the partial module
6. `b.py` tries `a.x` → AttributeError! (`x` hasn't been defined yet)

### Solutions:

```python
# Solution 1: Import inside functions (deferred)
# a.py
def get_b_value():
    import b
    return b.y

# Solution 2: Restructure to avoid the cycle
# Move shared code to a third module

# Solution 3: Import at end of module
# a.py
x = 10
import b   # now x exists when b tries to access it
```

---

## importlib.reload — hot-reloading modules

```python
import importlib
import mymodule

# Edit mymodule.py...

importlib.reload(mymodule)   # re-executes the module
# Warning: existing references to old objects are NOT updated
```

---

## `__import__` and `importlib.import_module`

```python
# Low-level: __import__ (don't use directly)
os = __import__("os")

# Clean API: importlib.import_module
import importlib
os = importlib.import_module("os")
sub = importlib.import_module("os.path")

# Dynamic: import by string name
module_name = "json"
mod = importlib.import_module(module_name)
print(mod.dumps({"hello": "world"}))
```

---

## Practice Exercises

1. **Write a finder** that loads Python modules from `.zip` files.
2. **Implement lazy importing** for a package with 20+ heavy submodules.
3. **Build an import hook** that automatically logs import times (which modules are slow to import).
4. **Create a sandboxed importer** that only allows importing from a whitelist of modules.
5. **Debug a circular import** — create one intentionally and fix it using three different strategies.
6. **Write a module reloader** that detects file changes and auto-reloads affected modules (hot reload for development).
