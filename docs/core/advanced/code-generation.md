---
title: Code Generation
description: compile(), exec(), dynamic code creation, template codegen and metaprogramming
---

# Code Generation <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 5</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 weeks</span>
    <span>📚 Prerequisites: <a href="ast-manipulation/">AST Manipulation</a>, <a href="metaclasses/">Metaclasses</a></span>
  </div>
</div>

---

## `compile()` — turning source/AST into executable code

```python
# From string
code = compile("x = 2 + 3", "<string>", "exec")
namespace = {}
exec(code, namespace)
print(namespace["x"])   # 5

# From AST
import ast
tree = ast.parse("result = sum(range(100))")
code = compile(tree, "<ast>", "exec")
ns = {}
exec(code, ns)
print(ns["result"])   # 4950
```

### compile() modes

| Mode | Input | Returns |
|---|---|---|
| `"exec"` | Module (multiple statements) | Code object for `exec()` |
| `"eval"` | Single expression | Code object for `eval()` |
| `"single"` | Single interactive statement | Code for REPL |

```python
# eval mode — returns a value
expr_code = compile("2 ** 10 + 1", "<expr>", "eval")
result = eval(expr_code)
print(result)   # 1025

# single mode — prints expression results (like REPL)
interactive = compile("42", "<input>", "single")
exec(interactive)   # prints: 42
```

---

## Generating classes dynamically

```python
def make_dataclass(class_name, fields):
    """Generate a class similar to @dataclass without the decorator."""

    # Build __init__
    init_args = ", ".join(fields)
    init_body = "\n    ".join(f"self.{f} = {f}" for f in fields)
    init_code = f"def __init__(self, {init_args}):\n    {init_body}"

    # Build __repr__
    repr_fields = ", ".join(f'{f}={{self.{f}!r}}' for f in fields)
    repr_code = f'def __repr__(self):\n    return f"{class_name}({repr_fields})"'

    # Build __eq__
    eq_checks = " and ".join(f"self.{f} == other.{f}" for f in fields)
    eq_code = f"def __eq__(self, other):\n    if type(self) != type(other): return NotImplemented\n    return {eq_checks}"

    # Execute in a clean namespace
    namespace = {}
    for code in [init_code, repr_code, eq_code]:
        exec(compile(code, f"<{class_name}>", "exec"), namespace)

    # Create the class
    cls = type(class_name, (), {
        "__init__": namespace["__init__"],
        "__repr__": namespace["__repr__"],
        "__eq__": namespace["__eq__"],
        "__slots__": tuple(fields),
    })
    return cls


Point = make_dataclass("Point", ["x", "y", "z"])

p1 = Point(1, 2, 3)
p2 = Point(1, 2, 3)
p3 = Point(4, 5, 6)

print(p1)          # Point(x=1, y=2, z=3)
print(p1 == p2)    # True
print(p1 == p3)    # False
```

!!! tip "This is what `@dataclass` actually does"
    The `dataclasses` module generates `__init__`, `__repr__`, `__eq__`, `__hash__`, `__lt__` etc. using code generation via `exec()`.

---

## Template-based code generation

```python
from string import Template
import textwrap

VALIDATOR_TEMPLATE = Template(textwrap.dedent('''
    def validate_${field_name}(value):
        """Auto-generated validator for ${field_name}."""
        if not isinstance(value, ${type_name}):
            raise TypeError(
                f"${field_name} must be ${type_name}, got {type(value).__name__}"
            )
        ${extra_checks}
        return value
'''))

def generate_validator(field_name, type_name, min_val=None, max_val=None):
    checks = []
    if min_val is not None:
        checks.append(f'if value < {min_val}: raise ValueError(f"{{value}} < {min_val}")')
    if max_val is not None:
        checks.append(f'if value > {max_val}: raise ValueError(f"{{value}} > {max_val}")')

    source = VALIDATOR_TEMPLATE.substitute(
        field_name=field_name,
        type_name=type_name,
        extra_checks="\n        ".join(checks) if checks else "pass",
    )

    namespace = {}
    exec(compile(source, f"<validator:{field_name}>", "exec"), namespace)
    return namespace[f"validate_{field_name}"]


# Generate validators
validate_age    = generate_validator("age", "int", min_val=0, max_val=150)
validate_name   = generate_validator("name", "str")
validate_score  = generate_validator("score", "float", min_val=0.0, max_val=100.0)

# Use them
print(validate_age(25))       # 25
print(validate_name("Alice")) # Alice

try:
    validate_age(-5)
except ValueError as ex:
    print(ex)   # -5 < 0

try:
    validate_score("high")
except TypeError as ex:
    print(ex)   # score must be float, got str
```

---

## Generating functions with closures (no exec needed)

```python
def make_getter(attr_name):
    """Generate an optimized getter function."""
    def getter(obj):
        return getattr(obj, attr_name)
    getter.__name__ = f"get_{attr_name}"
    getter.__qualname__ = f"get_{attr_name}"
    return getter

def make_setter(attr_name, validator=None):
    """Generate a setter with optional validation."""
    if validator:
        def setter(obj, value):
            validator(value)
            setattr(obj, attr_name, value)
    else:
        def setter(obj, value):
            setattr(obj, attr_name, value)
    setter.__name__ = f"set_{attr_name}"
    return setter


get_name = make_getter("name")
set_name = make_setter("name", validator=lambda v: None if isinstance(v, str) else (_ for _ in ()).throw(TypeError("must be str")))

class Person:
    def __init__(self, name):
        self.name = name

p = Person("Alice")
print(get_name(p))    # Alice
set_name(p, "Bob")
print(get_name(p))    # Bob
```

---

## Real-world code generation patterns

### Pattern 1: Protocol Buffers / Thrift

Tools like `protoc` generate Python classes from `.proto` schema files — these are essentially Python code generators.

### Pattern 2: ORM model generation

```python
def generate_model_class(table_name, columns):
    """Generate a SQLAlchemy-style model class dynamically."""
    attrs = {
        "__tablename__": table_name,
    }

    init_lines = []
    for col_name, col_type in columns.items():
        attrs[col_name] = None   # placeholder
        init_lines.append(f"        self.{col_name} = {col_name}")

    init_args = ", ".join(columns.keys())
    init_code = f"    def __init__(self, {init_args}):\n" + "\n".join(init_lines)

    namespace = {}
    exec(f"class {table_name.title()}:\n{init_code}", namespace)
    return namespace[table_name.title()]


User = generate_model_class("user", {
    "id": "int",
    "name": "str",
    "email": "str",
})

u = User(1, "Alice", "alice@example.com")
print(u.name)    # Alice
print(u.email)   # alice@example.com
```

### Pattern 3: API client generation from OpenAPI spec

```python
def generate_api_method(endpoint, method, params):
    """Generate a type-safe API method from spec."""
    param_str = ", ".join(f"{p['name']}: {p['type']}" for p in params)
    source = f'''
def {endpoint.replace("/", "_").strip("_")}(self, {param_str}):
    """Auto-generated: {method.upper()} {endpoint}"""
    return self._request("{method}", "{endpoint}", locals())
'''
    namespace = {}
    exec(source, namespace)
    return namespace[endpoint.replace("/", "_").strip("_")]
```

---

## Safety considerations

!!! warning "exec() and eval() are dangerous with untrusted input"

    ```python
    # NEVER do this with user input:
    user_code = input("Enter expression: ")
    result = eval(user_code)   # user could type: __import__('os').system('rm -rf /')
    ```

    If you must evaluate user expressions, use:
    - `ast.literal_eval()` — only evaluates literals (safe)
    - Sandboxed environments (Docker, RestrictedPython)
    - AST validation before compilation

```python
import ast

# Safe: only accepts literals
print(ast.literal_eval("[1, 2, 3]"))       # [1, 2, 3]
print(ast.literal_eval("{'a': True}"))     # {'a': True}

try:
    ast.literal_eval("__import__('os')")
except (ValueError, SyntaxError) as ex:
    print(f"Blocked: {ex}")   # Blocked: malformed node...
```

---

## Performance: generated code is fast

Code generated with `exec(compile(...))` runs at **full CPython speed** — it's real bytecode, same as hand-written code:

```python
import timeit

# Hand-written
def add_manual(a, b):
    return a + b

# Generated
exec("def add_generated(a, b):\n    return a + b")

# Same speed!
print(timeit.timeit("add_manual(1, 2)", globals=globals(), number=10_000_000))
print(timeit.timeit("add_generated(1, 2)", globals=globals(), number=10_000_000))
# Both ~0.5s — identical performance
```

---

## Practice Exercises

1. **Write a class factory** `make_struct(name, fields)` that generates a class with `__init__`, `__repr__`, `__eq__`, `__hash__`, and ordered comparison.
2. **Generate a dispatch table** from a dictionary mapping names to functions, creating a single efficient dispatch function.
3. **Build a simple DSL** that takes a configuration dict and generates a complete class with validation, serialization and deserialization.
4. **Implement `@jit_compile`** — a decorator that takes a function, reads its source with `inspect.getsource`, transforms the AST, and replaces it with an optimized version.
5. **Generate a REST API client** from an OpenAPI spec dict, with typed methods for each endpoint.
6. **Build a code generator** that reads a SQL schema and outputs complete Python model classes with type hints.
