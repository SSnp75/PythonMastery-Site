---
title: Typing & Type Hints
description: Annotations, generics, Protocol, TypeVar, overload, ParamSpec and mypy
---

# Typing & Type Hints <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisite: <a href="../competent/oop-fundamentals/">OOP Fundamentals</a></span>
  </div>
</div>

---

## Why type hints?

- Catch bugs **before runtime** with tools like `mypy`
- Serve as **living documentation**
- Enable **IDE autocompletion** and refactoring
- They're **optional** — Python doesn't enforce them at runtime

---

## Basic annotations

```python
# Variables
name: str = "Alice"
age: int = 30
score: float = 95.5
active: bool = True

# Functions
def greet(name: str, times: int = 1) -> str:
    return f"Hello, {name}! " * times

# None return
def log(message: str) -> None:
    print(message)
```

---

## Collection types

```python
# Python 3.9+ — use built-in types directly
names: list[str] = ["Alice", "Bob"]
scores: dict[str, int] = {"Alice": 95, "Bob": 87}
coords: tuple[float, float] = (3.0, 4.0)
unique: set[int] = {1, 2, 3}

# Variable-length tuple
values: tuple[int, ...] = (1, 2, 3, 4, 5)

# Nested
matrix: list[list[int]] = [[1, 2], [3, 4]]
config: dict[str, list[str]] = {"hosts": ["a", "b"]}
```

---

## Optional and Union

```python
from typing import Optional

# Optional[X] means X | None
def find_user(user_id: int) -> Optional[str]:
    if user_id == 1:
        return "Alice"
    return None

# Python 3.10+ syntax (preferred)
def find_user_v2(user_id: int) -> str | None:
    ...

# Union of multiple types
def process(value: int | str | float) -> str:
    return str(value)
```

---

## TypeVar — generic functions

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T:
    """Return first item — preserves the type."""
    return items[0]

# Type checkers infer:
x: int = first([1, 2, 3])       # T = int
y: str = first(["a", "b"])      # T = str

# Bounded TypeVar
from typing import Comparable
Num = TypeVar("Num", int, float)    # only int or float

def add(a: Num, b: Num) -> Num:
    return a + b

# Bound to a base class
from typing import TypeVar
T_Animal = TypeVar("T_Animal", bound="Animal")

def clone(animal: T_Animal) -> T_Animal:
    return type(animal)(animal.name)
```

---

## Generic classes

```python
from typing import TypeVar, Generic

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def peek(self) -> T:
        return self._items[-1]

    def is_empty(self) -> bool:
        return len(self._items) == 0

# Usage
int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push(2)
value: int = int_stack.pop()   # type checker knows this is int

str_stack: Stack[str] = Stack()
str_stack.push("hello")
```

---

## Protocol — structural subtyping (duck typing with types)

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    def draw(self, x: int, y: int) -> None: ...

class Circle:
    def draw(self, x: int, y: int) -> None:
        print(f"Drawing circle at ({x}, {y})")

class Square:
    def draw(self, x: int, y: int) -> None:
        print(f"Drawing square at ({x}, {y})")

class Text:
    def render(self) -> None:  # different method — NOT Drawable
        print("Rendering text")

def render_all(shapes: list[Drawable]) -> None:
    for shape in shapes:
        shape.draw(0, 0)

# Works — matches Protocol structurally
render_all([Circle(), Square()])

# Runtime checking (with @runtime_checkable)
print(isinstance(Circle(), Drawable))   # True
print(isinstance(Text(), Drawable))     # False
```

---

## Callable types

```python
from typing import Callable

# Function that takes (int, str) and returns bool
Predicate = Callable[[int, str], bool]

def apply(func: Callable[[int], int], value: int) -> int:
    return func(value)

result = apply(lambda x: x * 2, 5)   # 10

# Callback with no args
OnComplete = Callable[[], None]

def run_task(callback: OnComplete) -> None:
    # do work...
    callback()
```

---

## TypedDict — typed dictionaries

```python
from typing import TypedDict, NotRequired

class UserDict(TypedDict):
    name: str
    age: int
    email: NotRequired[str]   # optional key

# Type checker validates keys and value types
user: UserDict = {"name": "Alice", "age": 30}
user["email"] = "alice@example.com"   # OK
# user["phone"] = "555-1234"          # Error: extra key

def process_user(u: UserDict) -> str:
    return f"{u['name']} ({u['age']})"
```

---

## Literal types

```python
from typing import Literal

def set_direction(direction: Literal["north", "south", "east", "west"]) -> None:
    print(f"Moving {direction}")

set_direction("north")    # OK
# set_direction("up")     # Error: not a valid literal

Mode = Literal["r", "w", "a", "rb", "wb"]

def open_file(path: str, mode: Mode = "r") -> None:
    ...
```

---

## overload — multiple signatures

```python
from typing import overload

@overload
def process(value: int) -> str: ...
@overload
def process(value: str) -> int: ...
@overload
def process(value: list[int]) -> list[str]: ...

def process(value):
    """Actual implementation handles all cases."""
    if isinstance(value, int):
        return str(value)
    elif isinstance(value, str):
        return len(value)
    elif isinstance(value, list):
        return [str(x) for x in value]

# Type checker knows:
x: str = process(42)           # returns str
y: int = process("hello")     # returns int
z: list[str] = process([1,2]) # returns list[str]
```

---

## ParamSpec — preserving function signatures

```python
from typing import ParamSpec, TypeVar, Callable
from functools import wraps

P = ParamSpec("P")
R = TypeVar("R")

def logged(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator that preserves the original function's type signature."""
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@logged
def add(a: int, b: int) -> int:
    return a + b

# Type checker still sees: add(a: int, b: int) -> int
result: int = add(1, 2)
```

---

## TypeGuard — narrowing types

```python
from typing import TypeGuard

def is_string_list(values: list[object]) -> TypeGuard[list[str]]:
    """Returns True if all elements are strings."""
    return all(isinstance(v, str) for v in values)

def process(items: list[object]) -> None:
    if is_string_list(items):
        # Type checker now knows: items is list[str]
        print(", ".join(items))   # safe — all are strings
```

---

## Self type (Python 3.11+)

```python
from typing import Self

class Builder:
    def __init__(self) -> None:
        self.parts: list[str] = []

    def add(self, part: str) -> Self:
        self.parts.append(part)
        return self   # enables chaining

    def build(self) -> str:
        return " ".join(self.parts)

# Chaining works with proper types
result = Builder().add("Hello").add("World").build()
print(result)   # Hello World
```

---

## Running mypy

```bash
# Install
pip install mypy

# Check a file
mypy my_module.py

# Check a package
mypy src/

# Strict mode (catches more issues)
mypy --strict my_module.py

# Configuration in pyproject.toml
```

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
```

### Common mypy errors and fixes:

```python
# Error: Incompatible return value type (got "Optional[str]", expected "str")
def get_name() -> str:
    value = lookup()   # returns Optional[str]
    if value is None:
        return "Unknown"
    return value       # now mypy knows it's str

# Error: "dict[str, Any]" has no attribute "name"
# Fix: use TypedDict or a dataclass instead of plain dict
```

---

## Practice Exercises

1. **Annotate a complete module** with 10+ functions and run `mypy --strict` with zero errors.
2. **Write a generic `Result[T, E]`** type (like Rust's Result) with `Ok` and `Err` variants.
3. **Create a Protocol** for a database repository and implement it for SQLite and in-memory backends.
4. **Use `overload`** to type a function that behaves differently based on argument types.
5. **Write a typed decorator** using `ParamSpec` that preserves the decorated function's signature.
6. **Implement a generic `EventEmitter[T]`** class that's type-safe for event payloads.
