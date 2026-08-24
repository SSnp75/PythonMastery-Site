---
title: Python Execution Model
description: Frames, namespaces, LEGB scope, code objects and the eval loop
---

# Python Execution Model <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 5</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisite: <a href="bytecode/">Bytecode</a></span>
  </div>
</div>

---

## How Python executes your code

```
Source Code (.py)
    │
    ▼  [Parsing]
Abstract Syntax Tree (AST)
    │
    ▼  [Compilation]
Bytecode (code object)
    │
    ▼  [Execution]
CPython Virtual Machine (ceval.c)
    │
    ▼  [Result]
Output / Side Effects
```

Each step is accessible from Python:

```python
import ast, dis, types

source = """
x = 10
y = x + 5
print(y)
"""

# 1. Parse to AST
tree = ast.parse(source)
print(ast.dump(tree, indent=2))

# 2. Compile to code object
code = compile(source, "<demo>", "exec")
print(type(code))   # <class 'code'>

# 3. Disassemble bytecode
dis.dis(code)

# 4. Execute
exec(code)   # prints: 15
```

---

## Code Objects

Every function, module, class and comprehension has a code object:

```python
def example(a, b):
    """Add two numbers."""
    c = a + b
    return c

co = example.__code__

print(co.co_name)        # 'example'
print(co.co_filename)    # '<stdin>' or the file path
print(co.co_firstlineno) # line number of 'def'
print(co.co_varnames)    # ('a', 'b', 'c')
print(co.co_consts)      # (None, 'Add two numbers.')  — docstring is a const
print(co.co_argcount)    # 2
print(co.co_stacksize)   # max stack depth needed
print(co.co_nlocals)     # 3
print(co.co_flags)       # bit flags (optimized, generator, coroutine, etc.)

# co_code contains the raw bytecode bytes
print(co.co_code)        # b'd\x01S\x00' (opaque bytes)
```

### Code object attributes reference

| Attribute | Content |
|---|---|
| `co_name` | Function/class name |
| `co_varnames` | Local variable names (includes args) |
| `co_cellvars` | Variables captured by nested functions |
| `co_freevars` | Variables from enclosing scope |
| `co_consts` | Literal constants (numbers, strings, None, nested code objects) |
| `co_names` | Global and attribute names used |
| `co_stacksize` | Maximum operand stack depth |
| `co_flags` | Bitmap — CO_OPTIMIZED, CO_GENERATOR, CO_COROUTINE, etc. |

---

## Frame Objects

Every function call creates a frame. Frames are the runtime representation of code execution:

```python
import sys

def inner():
    frame = sys._getframe(0)   # current frame
    print(f"Function: {frame.f_code.co_name}")
    print(f"Line: {frame.f_lineno}")
    print(f"Locals: {frame.f_locals}")

    caller = frame.f_back       # caller's frame
    print(f"Caller: {caller.f_code.co_name}")
    print(f"Caller locals: {caller.f_locals}")

def outer():
    x = 42
    inner()

outer()
# Output:
# Function: inner
# Line: 5
# Locals: {'frame': <frame ...>}
# Caller: outer
# Caller locals: {'x': 42}
```

### Frame attributes

| Attribute | Content |
|---|---|
| `f_code` | Code object being executed |
| `f_locals` | Local variables dict |
| `f_globals` | Global variables dict |
| `f_builtins` | Built-in variables dict |
| `f_back` | Caller's frame (or None for top-level) |
| `f_lineno` | Current line number |
| `f_lasti` | Index of last bytecode instruction |

---

## The Call Stack

```python
import traceback

def c():
    traceback.print_stack()

def b():
    c()

def a():
    b()

a()
# Output:
#   File "demo.py", line 12, in <module> — a()
#   File "demo.py", line 10, in a        — b()
#   File "demo.py", line 7, in b         — c()
#   File "demo.py", line 4, in c         — traceback.print_stack()
```

Walking the stack programmatically:

```python
def walk_stack():
    frame = sys._getframe(0)
    while frame:
        print(f"  {frame.f_code.co_name} @ line {frame.f_lineno}")
        frame = frame.f_back
```

---

## LEGB Scope Resolution in Detail

```python
builtin_x = "B"   # would be in builtins, but for illustration

x = "Global"       # G

def outer():
    x = "Enclosing"  # E

    def inner():
        x = "Local"    # L
        print(x)       # → "Local"

    def inner2():
        print(x)       # → "Enclosing" (no local x)

    def inner3():
        # nonlocal lets you WRITE to enclosing scope
        nonlocal x
        x = "Modified by inner3"

    inner()
    inner2()
    inner3()
    print(x)          # → "Modified by inner3"

outer()
print(x)             # → "Global" (outer's x is different from global x)
```

### How the compiler decides scope at compile time

Python determines variable scope **at compile time**, not runtime:

```python
x = 10

def broken():
    print(x)    # UnboundLocalError!
    x = 20      # This assignment makes x LOCAL for the entire function

try:
    broken()
except UnboundLocalError as ex:
    print(ex)   # cannot access local variable 'x' where it is not associated with a value
```

The bytecode compiler sees the assignment `x = 20` and marks `x` as local for the **entire function body**, even before the assignment executes.

```python
import dis
dis.dis(broken)
# LOAD_FAST  x   ← looks in locals (not LOAD_GLOBAL!)
# ...
# STORE_FAST x
```

---

## global and nonlocal

```python
counter = 0

def increment():
    global counter    # tells compiler: counter is GLOBAL
    counter += 1

increment()
increment()
print(counter)   # 2


def make_counter():
    count = 0
    def inc():
        nonlocal count   # tells compiler: count is from ENCLOSING scope
        count += 1
        return count
    return inc

c = make_counter()
print(c())   # 1
print(c())   # 2
print(c())   # 3
```

---

## Cell Objects and Closures

When a function captures variables from an enclosing scope, Python uses **cells**:

```python
def outer():
    x = 10
    def inner():
        return x    # captures x
    return inner

fn = outer()

# The closure is stored as __closure__
print(fn.__closure__)              # (<cell object>,)
print(fn.__closure__[0].cell_contents)   # 10

# The code object knows which variables are free/cell
print(fn.__code__.co_freevars)     # ('x',)
```

---

## The Eval Loop (simplified)

CPython's main loop in `Python/ceval.c` is essentially:

```python
def eval_frame(frame):
    code = frame.f_code
    stack = []

    while True:
        opcode = next_instruction(frame)

        if opcode == LOAD_CONST:
            stack.append(code.co_consts[arg])

        elif opcode == LOAD_FAST:
            stack.append(frame.f_locals[code.co_varnames[arg]])

        elif opcode == STORE_FAST:
            frame.f_locals[code.co_varnames[arg]] = stack.pop()

        elif opcode == BINARY_ADD:
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b)

        elif opcode == RETURN_VALUE:
            return stack.pop()

        elif opcode == CALL_FUNCTION:
            args = [stack.pop() for _ in range(arg)]
            func = stack.pop()
            # Create new frame, recurse
            result = eval_frame(make_frame(func, args))
            stack.append(result)
```

---

## Execution of Modules

When Python imports or runs a module:

1. The module source is compiled to a code object
2. A module object is created
3. The code object is executed with the module's `__dict__` as both globals and locals
4. The resulting namespace becomes the module's attributes

```python
# This is approximately what 'import foo' does:
import importlib.util

spec = importlib.util.spec_from_file_location("foo", "foo.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)   # executes foo.py in module's namespace
```

---

## Practice Exercises

1. **Write a decorator** that prints the call stack depth before each function call.
2. **Implement a simple tracer** using `sys.settrace` that logs every function entry/exit.
3. **Walk the frame chain** and print all local variables at each level.
4. **Demonstrate the difference** between `LOAD_FAST`, `LOAD_GLOBAL`, `LOAD_DEREF` using `dis.dis`.
5. **Create a function** and modify its `__code__` to change a constant value without redefining it.
6. **Write a context manager** that temporarily patches a global variable and restores it on exit, using frame inspection.
