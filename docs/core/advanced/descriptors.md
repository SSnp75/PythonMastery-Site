---
title: Descriptors
description: "__get__, __set__, __delete__ — the mechanism behind @property, classmethod, staticmethod and ORMs"
---

# Descriptors <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 5</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="../competent/oop-fundamentals/">OOP Fundamentals</a></span>
  </div>
</div>

<div class="pm-next">
<strong>✅ What's next</strong>
<a href="metaclasses/">Metaclasses</a>
<a href="execution-model/">Execution Model</a>
</div>

---

## What is a descriptor?

A descriptor is any object that defines at least one of:

- `__get__(self, obj, objtype=None)` — intercept attribute read
- `__set__(self, obj, value)` — intercept attribute write
- `__delete__(self, obj)` — intercept attribute deletion

When a descriptor is assigned as a **class variable**, Python calls these methods automatically instead of returning the descriptor object itself.

```python
class Verbose:
    """A descriptor that logs every access."""

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self                      # class-level access
        value = obj.__dict__.get(self.name)
        print(f"  GET {self.name} → {value!r}")
        return value

    def __set__(self, obj, value):
        print(f"  SET {self.name} = {value!r}")
        obj.__dict__[self.name] = value

    def __delete__(self, obj):
        print(f"  DEL {self.name}")
        obj.__dict__.pop(self.name, None)


class Person:
    name = Verbose()
    age  = Verbose()

    def __init__(self, name, age):
        self.name = name      # triggers __set__
        self.age  = age


p = Person("Alice", 30)
# Output:
#   SET name = 'Alice'
#   SET age = 30

print(p.name)
# Output:
#   GET name → 'Alice'
#   Alice

del p.age
# Output:
#   DEL age
```

---

## Data Descriptors vs Non-data Descriptors

This distinction controls **priority** in attribute lookup.

| Type | Defines | Priority |
|---|---|---|
| **Data descriptor** | `__get__` AND (`__set__` or `__delete__`) | Higher than instance `__dict__` |
| **Non-data descriptor** | Only `__get__` | Lower than instance `__dict__` |

```python
class DataDesc:
    """Data descriptor — wins over instance __dict__."""
    def __get__(self, obj, objtype=None):
        return "from data descriptor"
    def __set__(self, obj, value):
        pass   # intercepts writes

class NonDataDesc:
    """Non-data descriptor — instance __dict__ can override."""
    def __get__(self, obj, objtype=None):
        return "from non-data descriptor"

class MyClass:
    data    = DataDesc()
    nondata = NonDataDesc()

obj = MyClass()
obj.__dict__["data"]    = "instance value"
obj.__dict__["nondata"] = "instance value"

print(obj.data)      # "from data descriptor"    ← descriptor wins
print(obj.nondata)   # "instance value"          ← instance wins
```

**Why this matters:** `@property` is a data descriptor (has `__set__`), which is why you can't accidentally override it with an instance variable.

---

## The Descriptor Resolution Order

When you access `obj.attr`, Python follows this lookup chain:

```
1. type(obj).__mro__  → search for data descriptor
2. obj.__dict__       → search instance dict
3. type(obj).__mro__  → search for non-data descriptor
4. Raise AttributeError
```

The actual CPython C implementation (simplified):

```python
def object_getattribute(obj, name):
    cls = type(obj)
    descriptor = None

    # Search the MRO for the name
    for base in cls.__mro__:
        if name in base.__dict__:
            descriptor = base.__dict__[name]
            break

    # Is it a data descriptor?
    desc_get = getattr(type(descriptor), '__get__', None)
    desc_set = getattr(type(descriptor), '__set__', None)

    if desc_get and desc_set:   # data descriptor
        return desc_get(descriptor, obj, cls)

    # Check instance dict
    if name in obj.__dict__:
        return obj.__dict__[name]

    # Non-data descriptor
    if desc_get:
        return desc_get(descriptor, obj, cls)

    # Plain class variable
    if descriptor is not None:
        return descriptor

    raise AttributeError(name)
```

---

## `__set_name__` — knowing your own name

Added in Python 3.6, called automatically when the class is created:

```python
class Field:
    def __set_name__(self, owner, name):
        self.public_name  = name
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name, None)

    def __set__(self, obj, value):
        setattr(obj, self.private_name, value)

class Point:
    x = Field()
    y = Field()

    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(3, 4)
print(p.x)                # 3
print(p.__dict__)         # {'_x': 3, '_y': 4}
print(Point.x)            # <Field object>
print(Point.x.public_name)  # 'x'
```

---

## Practical Use Case 1: Type-Validated Fields

```python
class Typed:
    def __init__(self, expected_type):
        self.expected_type = expected_type

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name} must be {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        obj.__dict__[self.name] = value

    def __delete__(self, obj):
        del obj.__dict__[self.name]


class Employee:
    name   = Typed(str)
    age    = Typed(int)
    salary = Typed(float)

    def __init__(self, name, age, salary):
        self.name   = name
        self.age    = age
        self.salary = salary

e = Employee("Alice", 30, 75000.0)
print(e.name)    # Alice
print(e.age)     # 30

try:
    e.age = "thirty"
except TypeError as ex:
    print(ex)    # age must be int, got str

try:
    Employee("Bob", "25", 50000.0)
except TypeError as ex:
    print(ex)    # age must be int, got str
```

---

## Practical Use Case 2: Range-Validated Fields

```python
class RangeChecked:
    def __init__(self, min_val=None, max_val=None):
        self.min_val = min_val
        self.max_val = max_val

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        if self.min_val is not None and value < self.min_val:
            raise ValueError(f"{self.name} must be >= {self.min_val}")
        if self.max_val is not None and value > self.max_val:
            raise ValueError(f"{self.name} must be <= {self.max_val}")
        obj.__dict__[self.name] = value


class Temperature:
    celsius = RangeChecked(min_val=-273.15, max_val=1e9)

    def __init__(self, celsius):
        self.celsius = celsius

    @property
    def fahrenheit(self):
        return self.celsius * 9/5 + 32

t = Temperature(100)
print(t.celsius)      # 100
print(t.fahrenheit)   # 212.0

try:
    Temperature(-300)
except ValueError as ex:
    print(ex)   # celsius must be >= -273.15
```

---

## Practical Use Case 3: Lazy/Cached Properties

```python
class Lazy:
    """Non-data descriptor that caches the result in instance __dict__."""

    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        # Compute once, then store in instance dict
        # Next access bypasses this descriptor (non-data!)
        value = self.func(obj)
        obj.__dict__[self.name] = value
        return value


class DataFile:
    def __init__(self, path):
        self.path = path

    @Lazy
    def contents(self):
        print(f"  Reading {self.path}...")
        with open(self.path) as f:
            return f.read()

# First access computes
df = DataFile("config.txt")
# print(df.contents)  → "Reading config.txt..."
# print(df.contents)  → returns cached, no print
```

!!! tip "This is how `functools.cached_property` works"
    Python 3.8+ includes `@cached_property` which is exactly this pattern.

---

## How @property Works Under the Hood

`property` is a data descriptor class built into Python:

```python
class property:
    """Simplified reimplementation of the built-in property."""

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc or (fget.__doc__ if fget else None)

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError(f"property '{self.name}' has no getter")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError(f"property '{self.name}' is read-only")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError(f"property '{self.name}' cannot be deleted")
        self.fdel(obj)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)
```

Now you understand why `@property` is more than magic — it's just a descriptor.

---

## How @classmethod and @staticmethod Work

```python
class classmethod:
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        if objtype is None:
            objtype = type(obj)
        def wrapper(*args, **kwargs):
            return self.func(objtype, *args, **kwargs)
        return wrapper


class staticmethod:
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        return self.func   # just return the raw function
```

Regular methods are also descriptors — `function.__get__` binds `self`:

```python
class Foo:
    def bar(self):
        pass

print(type(Foo.__dict__['bar']))   # <class 'function'>
print(Foo.bar)                     # <function Foo.bar>

f = Foo()
print(f.bar)    # <bound method Foo.bar of <Foo object>>
# This is function.__get__(f, Foo) returning a bound method
```

---

## Descriptors and `__slots__`

When a class uses `__slots__`, Python creates **member descriptors** for each slot:

```python
class Compact:
    __slots__ = ('x', 'y')

print(type(Compact.x))   # <class 'member_descriptor'>

c = Compact()
c.x = 10
print(c.x)    # 10

# No __dict__ exists
try:
    c.__dict__
except AttributeError:
    print("No __dict__ — slots only")
```

Member descriptors are data descriptors implemented in C — extremely fast.

---

## Composing Descriptors (Stacking Validators)

```python
class Validator:
    """Base class for chainable validators."""
    def __init__(self):
        self.validators = []

    def __set_name__(self, owner, name):
        self.name = name

    def add_validator(self, func):
        self.validators.append(func)
        return self

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        for validate in self.validators:
            validate(self.name, value)
        obj.__dict__[self.name] = value


def typed(expected):
    def check(name, value):
        if not isinstance(value, expected):
            raise TypeError(f"{name}: expected {expected.__name__}, got {type(value).__name__}")
    return check

def positive(name, value):
    if value <= 0:
        raise ValueError(f"{name}: must be positive, got {value}")


class Product:
    name  = Validator()
    price = Validator()

    name.add_validator(typed(str))
    price.add_validator(typed((int, float)))
    price.add_validator(positive)

    def __init__(self, name, price):
        self.name = name
        self.price = price

p = Product("Widget", 9.99)
print(p.name, p.price)   # Widget 9.99

try:
    Product("Free", -5)
except ValueError as ex:
    print(ex)   # price: must be positive, got -5
```

---

## Descriptor Best Practices

!!! tip "Rules of thumb"

    1. **Use `__set_name__`** — don't require the user to pass the field name manually
    2. **Store data in `obj.__dict__`** — not in the descriptor itself (otherwise all instances share one value)
    3. **Return `self` when `obj is None`** — allows class-level introspection
    4. **Make it a data descriptor if you need to validate writes** — add `__set__`
    5. **Make it a non-data descriptor for caching** — allows instance dict to override

---

## Real-World Descriptor Usage

| Library/Framework | What uses descriptors |
|---|---|
| SQLAlchemy | `Column()` mapped attributes |
| Django ORM | `Field()` model fields |
| Pydantic v1 | `Field()` validators |
| attrs / dataclasses | Generated `__init__` uses `__set_name__` |
| `functools.cached_property` | Non-data descriptor for caching |
| Built-in `property` | Data descriptor |
| Built-in `classmethod` | Non-data descriptor |
| Built-in `staticmethod` | Non-data descriptor |
| Functions | `function.__get__` creates bound methods |

---

## Practice Exercises

1. **Write a `Positive` descriptor** that only allows positive numbers, raising `ValueError` otherwise.
2. **Implement `@cached_property`** from scratch as a non-data descriptor.
3. **Write a `ReadOnly` descriptor** that allows setting once in `__init__` but raises `AttributeError` on subsequent writes.
4. **Write an `Audited` descriptor** that keeps a history of all values ever assigned, accessible via `MyClass.field.history(obj)`.
5. **Reimplement `@property`** with full `getter`, `setter`, `deleter` chaining.
6. **Build an ORM-style `Column` descriptor** that tracks dirty fields for SQL UPDATE generation.
