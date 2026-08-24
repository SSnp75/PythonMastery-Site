---
title: Context Managers
description: "with statement, __enter__/__exit__, contextlib, async context managers and real-world patterns"
---

# Context Managers <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisite: <a href="decorators/">Decorators</a></span>
  </div>
</div>

---

## The `with` statement protocol

When you write `with X as Y:`, Python calls:

1. `X.__enter__()` → return value assigned to `Y`
2. Execute the body
3. `X.__exit__(exc_type, exc_val, exc_tb)` → cleanup (always called, even on exception)

```python
# This:
with open("file.txt") as f:
    data = f.read()

# Is equivalent to:
f = open("file.txt")
f.__enter__()
try:
    data = f.read()
finally:
    f.__exit__(None, None, None)
```

---

## Writing your own (class-based)

```python
import time

class Timer:
    """Measure elapsed time of a code block."""

    def __init__(self, label="Block"):
        self.label = label

    def __enter__(self):
        self.start = time.perf_counter()
        return self   # the 'as' variable

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self.start
        print(f"  {self.label}: {self.elapsed:.4f}s")
        return False   # don't suppress exceptions


with Timer("Computation"):
    total = sum(range(10_000_000))
# Output: Computation: 0.3412s

# Access elapsed time after
with Timer("Fast") as t:
    x = 2 ** 1000
print(f"That took {t.elapsed:.6f}s")
```

---

## Exception handling in `__exit__`

```python
class Suppressor:
    """Suppress specific exceptions."""

    def __init__(self, *exceptions):
        self.exceptions = exceptions

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            if issubclass(exc_type, self.exceptions):
                print(f"  Suppressed: {exc_type.__name__}: {exc_val}")
                return True    # SUPPRESS the exception
        return False           # DON'T suppress — let it propagate


with Suppressor(FileNotFoundError, PermissionError):
    open("nonexistent.txt")   # would normally crash
    print("This still prints!")
# Output: Suppressed: FileNotFoundError: [Errno 2] No such file or directory...
# Program continues normally
```

The return value of `__exit__`:
- `True` → **suppress** the exception (code continues after `with` block)
- `False` / `None` → **propagate** the exception (normal behavior)

---

## Generator-based context managers with `contextlib`

```python
from contextlib import contextmanager

@contextmanager
def managed_file(path, mode="r"):
    """Open a file and ensure it's closed."""
    f = open(path, mode)
    try:
        yield f          # value given to 'as' variable
    finally:
        f.close()        # always runs

with managed_file("data.txt", "w") as f:
    f.write("Hello!")
```

### The pattern:

```python
@contextmanager
def my_context():
    # SETUP (runs before 'with' body)
    resource = acquire()
    try:
        yield resource       # hand control to 'with' body
    except Exception:
        handle_error()
        raise                # re-raise by default
    finally:
        # TEARDOWN (always runs)
        release(resource)
```

---

## Real-world patterns

### Temporary working directory

```python
import os
from contextlib import contextmanager

@contextmanager
def working_directory(path):
    """Temporarily change working directory."""
    original = os.getcwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(original)

with working_directory("/tmp"):
    print(os.getcwd())   # /tmp
print(os.getcwd())       # back to original
```

### Database transaction

```python
@contextmanager
def transaction(connection):
    """Commit on success, rollback on exception."""
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

with transaction(get_connection()) as conn:
    conn.execute("INSERT INTO users VALUES (?, ?)", (1, "Alice"))
    conn.execute("INSERT INTO users VALUES (?, ?)", (2, "Bob"))
    # Both committed, or both rolled back on error
```

### Temporary environment variable

```python
import os
from contextlib import contextmanager

@contextmanager
def env_var(key, value):
    """Set env var temporarily, restore on exit."""
    old = os.environ.get(key)
    os.environ[key] = value
    try:
        yield
    finally:
        if old is None:
            del os.environ[key]
        else:
            os.environ[key] = old

with env_var("DATABASE_URL", "sqlite:///test.db"):
    print(os.environ["DATABASE_URL"])   # sqlite:///test.db
# Restored to original
```

### Redirecting stdout

```python
import sys
from io import StringIO
from contextlib import contextmanager

@contextmanager
def capture_stdout():
    """Capture all print output."""
    old = sys.stdout
    sys.stdout = StringIO()
    try:
        yield sys.stdout
    finally:
        sys.stdout = old

with capture_stdout() as output:
    print("This is captured")
    print("So is this")

captured = output.getvalue()
print(f"Got: {captured!r}")
# Got: 'This is captured\nSo is this\n'
```

---

## contextlib utilities

### suppress — catch and ignore exceptions

```python
from contextlib import suppress
import os

# Instead of try/except/pass:
with suppress(FileNotFoundError):
    os.remove("maybe_exists.txt")

# Equivalent to:
try:
    os.remove("maybe_exists.txt")
except FileNotFoundError:
    pass
```

### redirect_stdout / redirect_stderr

```python
from contextlib import redirect_stdout
from io import StringIO

f = StringIO()
with redirect_stdout(f):
    print("captured!")
print(f.getvalue())   # "captured!\n"
```

### closing — add close() to objects without context manager

```python
from contextlib import closing
from urllib.request import urlopen

with closing(urlopen("https://example.com")) as page:
    content = page.read()
```

### ExitStack — dynamic context manager composition

```python
from contextlib import ExitStack

def process_files(file_list):
    """Open multiple files dynamically."""
    with ExitStack() as stack:
        files = [stack.enter_context(open(f)) for f in file_list]
        # All files guaranteed to close, even if one fails
        for f in files:
            print(f.readline())

process_files(["a.txt", "b.txt", "c.txt"])
```

### nullcontext — a no-op context manager

```python
from contextlib import nullcontext

def process(data, lock=None):
    """Optionally use a lock."""
    with lock or nullcontext():
        # If lock is None, this is just pass-through
        return expensive_computation(data)
```

---

## Nested and multiple context managers

```python
# Multiple in one line
with open("input.txt") as fin, open("output.txt", "w") as fout:
    fout.write(fin.read().upper())

# Python 3.10+ parenthesized context managers
with (
    open("a.txt") as a,
    open("b.txt") as b,
    open("c.txt", "w") as out,
):
    out.write(a.read() + b.read())
```

---

## Async context managers

```python
import asyncio

class AsyncTimer:
    async def __aenter__(self):
        import time
        self.start = time.perf_counter()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        import time
        self.elapsed = time.perf_counter() - self.start
        print(f"  Async block: {self.elapsed:.4f}s")
        return False

async def main():
    async with AsyncTimer():
        await asyncio.sleep(1)
    # Output: Async block: 1.0012s

asyncio.run(main())
```

### Generator-based async context manager:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def async_db_connection(url):
    conn = await connect(url)
    try:
        yield conn
    finally:
        await conn.close()

async def main():
    async with async_db_connection("postgres://localhost/db") as conn:
        result = await conn.fetch("SELECT * FROM users")
```

---

## Reentrant vs reusable context managers

```python
# REENTRANT: can be used in nested 'with' statements
# Example: suppress(), redirect_stdout()
from contextlib import suppress
cm = suppress(ValueError)
with cm:
    with cm:   # OK — reentrant
        int("not a number")

# REUSABLE: can be used multiple times (but not nested)
# Example: Your custom Timer class
t = Timer("test")
with t:
    pass
with t:    # OK — reusable
    pass

# SINGLE-USE: can only be used once
# Example: most @contextmanager generators
@contextmanager
def single_use():
    print("setup")
    yield
    print("teardown")

cm = single_use()
with cm: pass
# with cm: pass   # ERROR — generator already exhausted
```

---

## Practice Exercises

1. **Write a `Retry` context manager** that retries the block up to N times if it raises a specific exception.
2. **Write a `TempFile` context manager** that creates a temporary file, yields it, and deletes it on exit.
3. **Write a `Profiler` context manager** that measures CPU time, memory allocated, and function calls.
4. **Write an `atomic_write`** context manager that writes to a temp file and renames on success (atomic file updates).
5. **Use `ExitStack`** to open a variable number of files and merge their contents.
6. **Write an async context manager** for a connection pool that checks out/returns connections.
