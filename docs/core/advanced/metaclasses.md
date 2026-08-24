---
title: Metaclasses
description: "type, __new__, __init_subclass__, __prepare__ and controlling class creation"
---

# Metaclasses <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 5</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="descriptors/">Descriptors</a></span>
  </div>
</div>

---

## The fundamental truth: classes are objects

In Python, everything is an object — including classes. A class is an instance of its metaclass.

```python
class Dog:
    pass

print(type(Dog))       # <class 'type'>
print(type(Dog()))     # <class '__main__.Dog'>

# type(instance) → class
# type(class)    → metaclass
# type(type)     → type  (it's its own metaclass!)
```

---

## Creating classes dynamically with `type()`

`type` has a dual role — as a function it returns the type of an object; with three arguments it **creates a new class**:

```python
# type(name, bases, namespace)

def bark(self):
    return f"{self.name} says Woof!"

Dog = type("Dog", (), {
    "species": "Canis familiaris",
    "bark": bark,
    "__init__": lambda self, name: setattr(self, "name", name),
})

rex = Dog("Rex")
print(rex.bark())        # Rex says Woof!
print(Dog.species)       # Canis familiaris
print(type(rex))         # <class '__main__.Dog'>
print(type(Dog))         # <class 'type'>
```

This is **exactly** what the `class` statement does under the hood.

---

## How class creation works (step by step)

When Python encounters:

```python
class Foo(Base, metaclass=Meta):
    x = 10
    def method(self): ...
```

It executes these steps:

```python
# 1. Determine metaclass
metaclass = Meta   # (or type if not specified)

# 2. Prepare the namespace
namespace = metaclass.__prepare__("Foo", (Base,))   # usually returns dict

# 3. Execute the class body inside that namespace
exec(body, globals(), namespace)
# Now namespace = {"x": 10, "method": <function>}

# 4. Call the metaclass to create the class object
Foo = metaclass("Foo", (Base,), namespace)
# This calls metaclass.__new__ then metaclass.__init__
```

---

## Writing a custom metaclass

```python
class Meta(type):
    """Metaclass that prints when classes are created."""

    def __new__(mcs, name, bases, namespace):
        print(f"  Creating class: {name}")
        print(f"  Bases: {bases}")
        print(f"  Attributes: {list(namespace.keys())}")
        cls = super().__new__(mcs, name, bases, namespace)
        return cls

    def __init__(cls, name, bases, namespace):
        print(f"  Initializing class: {name}")
        super().__init__(name, bases, namespace)


class Animal(metaclass=Meta):
    sound = "..."

# Output:
#   Creating class: Animal
#   Bases: ()
#   Attributes: ['__module__', '__qualname__', 'sound']
#   Initializing class: Animal

class Dog(Animal):
    sound = "Woof"

# Output:
#   Creating class: Dog
#   Bases: (<class 'Animal'>,)
#   Attributes: ['__module__', '__qualname__', 'sound']
#   Initializing class: Dog
```

---

## `__new__` vs `__init__` in metaclasses

| Method | Called on | Purpose |
|---|---|---|
| `Meta.__new__(mcs, name, bases, ns)` | The metaclass | **Creates** the class object |
| `Meta.__init__(cls, name, bases, ns)` | The new class | **Initializes** the class after creation |
| `Meta.__call__(cls, *args, **kwargs)` | The class | Called when you **instantiate** `Foo()` |

```python
class SingletonMeta(type):
    """Each class created with this metaclass has at most one instance."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Call type.__call__ which calls cls.__new__ + cls.__init__
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Database(metaclass=SingletonMeta):
    def __init__(self, url="sqlite:///app.db"):
        self.url = url
        print(f"  Connecting to {url}")

db1 = Database("postgres://localhost/mydb")
# Output: Connecting to postgres://localhost/mydb

db2 = Database("mysql://other")
# No output — same instance returned

print(db1 is db2)       # True
print(db2.url)          # postgres://localhost/mydb  (first call's value)
```

---

## `__prepare__` — controlling the namespace

`__prepare__` returns the dict-like object used for the class body. You can use this to customize how the body is evaluated.

```python
from collections import OrderedDict

class OrderedMeta(type):
    @classmethod
    def __prepare__(mcs, name, bases):
        return OrderedDict()

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, dict(namespace))
        cls._fields = [k for k in namespace if not k.startswith('_')]
        return cls


class Record(metaclass=OrderedMeta):
    name = ""
    age  = 0
    city = ""

print(Record._fields)   # ['name', 'age', 'city']  — preserves definition order
```

!!! note "Python 3.7+ dicts are ordered"
    Since Python 3.7, regular dicts maintain insertion order, so `__prepare__` returning `OrderedDict` is less necessary. But the mechanism is still useful for other things like logging or validating definitions.

---

## Use Case: Auto-registering plugins

```python
class PluginMeta(type):
    registry = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        # Don't register the base class itself
        if bases:
            mcs.registry[name] = cls
        return cls


class Plugin(metaclass=PluginMeta):
    """Base class for all plugins."""
    pass


class PDFExporter(Plugin):
    def export(self, data):
        return f"PDF: {data}"

class CSVExporter(Plugin):
    def export(self, data):
        return f"CSV: {data}"

class JSONExporter(Plugin):
    def export(self, data):
        return f"JSON: {data}"


print(PluginMeta.registry)
# {'PDFExporter': <class 'PDFExporter'>,
#  'CSVExporter': <class 'CSVExporter'>,
#  'JSONExporter': <class 'JSONExporter'>}

# Dynamic plugin loading
def get_exporter(name):
    return PluginMeta.registry[name]()

exporter = get_exporter("PDFExporter")
print(exporter.export("hello"))   # PDF: hello
```

---

## Use Case: Interface enforcement

```python
class InterfaceMeta(type):
    """Metaclass that enforces subclasses implement required methods."""

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)

        # Skip the base class
        if bases:
            required = getattr(cls, '_required_methods', [])
            for method_name in required:
                if method_name not in namespace:
                    raise TypeError(
                        f"Class '{name}' must implement '{method_name}'"
                    )
        return cls


class Serializer(metaclass=InterfaceMeta):
    _required_methods = ['serialize', 'deserialize']


# This works:
class JSONSerializer(Serializer):
    def serialize(self, obj):
        import json
        return json.dumps(obj)

    def deserialize(self, data):
        import json
        return json.loads(data)


# This raises TypeError at class DEFINITION time (not instantiation):
try:
    class BrokenSerializer(Serializer):
        def serialize(self, obj):
            return str(obj)
        # Missing deserialize!
except TypeError as ex:
    print(ex)   # Class 'BrokenSerializer' must implement 'deserialize'
```

---

## Use Case: Automatic `__repr__` and `__eq__`

```python
class AutoMeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)

        # Find annotated fields
        annotations = namespace.get('__annotations__', {})
        if annotations:
            fields = list(annotations.keys())

            def __repr__(self):
                values = ", ".join(f"{f}={getattr(self, f)!r}" for f in fields)
                return f"{name}({values})"

            def __eq__(self, other):
                if type(self) != type(other):
                    return NotImplemented
                return all(getattr(self, f) == getattr(other, f) for f in fields)

            cls.__repr__ = __repr__
            cls.__eq__   = __eq__

        return cls


class Point(metaclass=AutoMeta):
    x: float
    y: float

    def __init__(self, x, y):
        self.x = x
        self.y = y

p1 = Point(3.0, 4.0)
p2 = Point(3.0, 4.0)
p3 = Point(1.0, 2.0)

print(p1)          # Point(x=3.0, y=4.0)
print(p1 == p2)    # True
print(p1 == p3)    # False
```

!!! tip "This is essentially what `@dataclass` does"
    The `@dataclass` decorator uses similar introspection (though it's a decorator, not a metaclass).

---

## `__init_subclass__` — the simpler alternative (Python 3.6+)

For most metaclass use cases, `__init_subclass__` is simpler and sufficient:

```python
class Plugin:
    _registry = {}

    def __init_subclass__(cls, plugin_name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        name = plugin_name or cls.__name__
        cls._registry[name] = cls

class PDF(Plugin, plugin_name="pdf"):
    pass

class CSV(Plugin, plugin_name="csv"):
    pass

print(Plugin._registry)
# {'pdf': <class 'PDF'>, 'csv': <class 'CSV'>}
```

**When to use `__init_subclass__` vs metaclass:**

| Need | Use |
|---|---|
| Register subclasses | `__init_subclass__` |
| Validate class at creation time | `__init_subclass__` |
| Modify class namespace before execution | Metaclass + `__prepare__` |
| Control instantiation (`__call__`) | Metaclass |
| Change how attributes are stored | Metaclass |

---

## Metaclass conflicts and resolution

```python
class MetaA(type): pass
class MetaB(type): pass

class A(metaclass=MetaA): pass
class B(metaclass=MetaB): pass

# This raises TypeError:
try:
    class C(A, B): pass
except TypeError as ex:
    print(ex)
    # metaclass conflict: the metaclass of a derived class must be a
    # (non-strict) subclass of the metaclasses of all its bases

# Solution: create a combined metaclass
class MetaC(MetaA, MetaB): pass
class C(A, B, metaclass=MetaC): pass   # works!
```

---

## Real-world metaclass usage

| Library | What it does with metaclasses |
|---|---|
| Django ORM | `Model` uses `ModelBase` metaclass to collect field definitions |
| SQLAlchemy (classic) | `DeclarativeMeta` maps classes to database tables |
| Enum | `EnumMeta` controls how enum members are created |
| ABCMeta | `ABCMeta` tracks abstract methods |
| Protocol (typing) | Uses metaclass for structural type checking |

---

## When NOT to use metaclasses

!!! warning "Metaclasses are powerful but complex"
    Before reaching for a metaclass, try these simpler alternatives:

    1. **Class decorators** — modify a class after creation
    2. **`__init_subclass__`** — hook into subclass creation
    3. **Descriptors** — control attribute access
    4. **`__set_name__`** — configure descriptors at class creation

    Use metaclasses only when you need to:
    - Control the namespace before class body executes (`__prepare__`)
    - Intercept instantiation across all subclasses (`__call__`)
    - Do something that can't be done after the class exists

---

## Practice Exercises

1. **Write a `FrozenMeta`** that makes all attributes read-only after `__init__` completes.
2. **Write a `ValidatedMeta`** that checks all methods have type annotations.
3. **Implement the Singleton pattern** using a metaclass `__call__`.
4. **Write an `AbstractMeta`** that raises `TypeError` if a class with abstract methods is instantiated (reimplement `ABCMeta`).
5. **Write a `TrackedMeta`** that counts how many instances of each class exist.
6. **Use `__prepare__`** to detect duplicate method definitions in a class body.
