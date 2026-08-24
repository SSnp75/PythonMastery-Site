---
title: Pythonic Patterns
description: Python-specific patterns that differ from traditional GoF — protocols, mixins, descriptors, context managers as patterns
---

# Pythonic Patterns <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🏗️ Design Patterns · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
  </div>
</div>

---

## Why Python patterns differ from GoF

The Gang of Four patterns were designed for C++ and Java — languages with:
- No first-class functions
- No duck typing
- No multiple inheritance
- No decorators or context managers

Python has all of these, making many classic patterns unnecessary or much simpler.

---

## Strategy → just use functions

```python
# Java-style strategy (unnecessary in Python)
class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data): ...

class BubbleSort(SortStrategy): ...
class QuickSort(SortStrategy): ...

# Pythonic — functions ARE strategies
def process(data, sort_fn=sorted):
    return sort_fn(data)

process(data, sort_fn=lambda x: sorted(x, reverse=True))
process(data, sort_fn=heapq.nsmallest)
```

---

## Singleton → module-level instance

```python
# Don't use metaclass singletons. Just use a module.

# database.py
class _Database:
    def __init__(self):
        self.connection = None
    def connect(self, url):
        self.connection = create_connection(url)

db = _Database()   # THE instance

# Everyone imports the same object:
# from database import db
# db.connect("postgres://...")
```

---

## Mixin pattern — reusable behavior via multiple inheritance

```python
import json
from datetime import datetime

class TimestampMixin:
    """Adds created_at / updated_at tracking."""
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        original_init = cls.__init__

        def new_init(self, *args, **kw):
            original_init(self, *args, **kw)
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
        cls.__init__ = new_init

    def touch(self):
        self.updated_at = datetime.utcnow()

class SerializableMixin:
    """Adds to_dict() and to_json() methods."""
    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)

class ValidatableMixin:
    """Adds validate() that checks _validators class attribute."""
    def validate(self) -> list[str]:
        errors = []
        for field, validator in getattr(self.__class__, "_validators", {}).items():
            value = getattr(self, field, None)
            error = validator(value)
            if error:
                errors.append(f"{field}: {error}")
        return errors

# Compose behaviors
class User(TimestampMixin, SerializableMixin, ValidatableMixin):
    _validators = {
        "name": lambda v: "required" if not v else None,
        "email": lambda v: "invalid" if v and "@" not in v else None,
    }

    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

u = User("Alice", "alice@example.com")
print(u.to_json())          # {"name": "Alice", "email": "...", "created_at": "..."}
print(u.validate())         # []
print(u.created_at)         # 2026-08-23 ...

bad_user = User("", "invalid")
print(bad_user.validate())  # ['name: required', 'email: invalid']
```

---

## Registry pattern — auto-register subclasses

```python
class Serializer:
    """Base class that auto-registers all serializers by format name."""
    _registry: dict[str, type] = {}

    def __init_subclass__(cls, format_name: str = "", **kwargs):
        super().__init_subclass__(**kwargs)
        if format_name:
            cls._registry[format_name] = cls

    @classmethod
    def get(cls, format_name: str) -> "Serializer":
        klass = cls._registry.get(format_name)
        if not klass:
            raise ValueError(f"Unknown format: {format_name}. Available: {list(cls._registry)}")
        return klass()

class JSONSerializer(Serializer, format_name="json"):
    def serialize(self, data): return json.dumps(data)
    def deserialize(self, raw): return json.loads(raw)

class CSVSerializer(Serializer, format_name="csv"):
    def serialize(self, data): return "\n".join(",".join(map(str, row)) for row in data)
    def deserialize(self, raw): return [line.split(",") for line in raw.splitlines()]

class YAMLSerializer(Serializer, format_name="yaml"):
    def serialize(self, data): import yaml; return yaml.dump(data)
    def deserialize(self, raw): import yaml; return yaml.safe_load(raw)

# Usage — no if/elif chain!
serializer = Serializer.get("json")
output = serializer.serialize({"name": "Alice"})
print(output)   # '{"name": "Alice"}'

print(Serializer._registry)   # {'json': JSONSerializer, 'csv': CSVSerializer, 'yaml': YAMLSerializer}
```

---

## Context manager as resource pattern

```python
from contextlib import contextmanager

@contextmanager
def database_transaction(connection):
    """Pattern: resource acquisition + guaranteed cleanup."""
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()

@contextmanager
def temporary_setting(obj, attr, value):
    """Pattern: temporary modification + restore."""
    original = getattr(obj, attr)
    setattr(obj, attr, value)
    try:
        yield
    finally:
        setattr(obj, attr, original)
```

---

## Descriptor as validator pattern

```python
class Validated:
    """Reusable field validator — use as class attribute."""
    def __init__(self, validator, error_msg="Invalid value"):
        self.validator = validator
        self.error_msg = error_msg

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None: return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        if not self.validator(value):
            raise ValueError(f"{self.name}: {self.error_msg} (got {value!r})")
        obj.__dict__[self.name] = value

# Reusable validators
def positive(v): return isinstance(v, (int, float)) and v > 0
def non_empty_str(v): return isinstance(v, str) and len(v.strip()) > 0
def valid_email(v): return isinstance(v, str) and "@" in v and "." in v

class Product:
    name  = Validated(non_empty_str, "must be non-empty string")
    price = Validated(positive, "must be positive number")
    email = Validated(valid_email, "must be valid email")

    def __init__(self, name, price, email):
        self.name = name
        self.price = price
        self.email = email

p = Product("Widget", 9.99, "a@b.com")   # OK

try:
    Product("", 9.99, "a@b.com")
except ValueError as e:
    print(e)   # name: must be non-empty string (got '')
```

---

## Practice Exercises

1. **Rewrite 3 GoF patterns** using Python idioms (functions, protocols, decorators).
2. **Build a mixin library** — TimestampMixin, AuditMixin, SoftDeleteMixin, CacheMixin.
3. **Implement a plugin registry** using `__init_subclass__` and demonstrate dynamic loading.
4. **Use descriptors** to build a validated model class (like a mini-Pydantic).
5. **Compare**: write the same feature using GoF Strategy (class hierarchy) vs Pythonic (first-class functions).
