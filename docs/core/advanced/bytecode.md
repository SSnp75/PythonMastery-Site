---
title: Bytecode
description: dis module, .pyc files, opcodes and understanding compiled Python
---

# Bytecode <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 5</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="../beginner/functions/">Functions</a></span>
  </div>
</div>

---

## What is bytecode?

Python source is compiled to **bytecode** — a low-level, platform-independent instruction set executed by the CPython virtual machine. Each instruction is 2 bytes: an opcode + an argument.

```python
def add(a, b):
    return a + b
```

Compiles to:

```python
import dis
dis.dis(add)
```

Output:
```
  2           0 LOAD_FAST                0 (a)
              2 LOAD_FAST                1 (b)
              4 BINARY_ADD
              6 RETURN_VALUE
```

Each line: `line_number | byte_offset | OPCODE | arg_index (human_name)`

---

## The `dis` module in depth

```python
import dis

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

dis.dis(factorial)
```

Output:
```
  2           0 LOAD_FAST                0 (n)
              2 LOAD_CONST               1 (1)
              4 COMPARE_OP               1 (<=)
              6 POP_JUMP_IF_FALSE       12

  3           8 LOAD_CONST               1 (1)
             10 RETURN_VALUE

  4     >>   12 LOAD_FAST                0 (n)
             14 LOAD_GLOBAL              0 (factorial)
             16 LOAD_FAST                0 (n)
             18 LOAD_CONST               1 (1)
             20 BINARY_SUBTRACT
             22 CALL_FUNCTION            1
             24 BINARY_MULTIPLY
             26 RETURN_VALUE
```

### Reading the output

- `LOAD_FAST 0 (n)` — push local variable #0 (named `n`) onto the stack
- `LOAD_CONST 1 (1)` — push constant #1 (value `1`) from `co_consts`
- `COMPARE_OP 1 (<=)` — pop two values, compare, push bool result
- `POP_JUMP_IF_FALSE 12` — if top of stack is False, jump to byte 12
- `CALL_FUNCTION 1` — call function with 1 argument
- `BINARY_MULTIPLY` — pop two values, multiply, push result
- `>>` — jump target marker

---

## Key opcode categories

### Loading values onto the stack

| Opcode | Source | Speed |
|---|---|---|
| `LOAD_CONST` | `co_consts` tuple | Fastest |
| `LOAD_FAST` | Local variables (array) | Very fast |
| `LOAD_DEREF` | Closure cells | Fast |
| `LOAD_GLOBAL` | Module globals dict | Moderate |
| `LOAD_ATTR` | Object attribute | Slowest (involves lookup) |

### Storing values

| Opcode | Destination |
|---|---|
| `STORE_FAST` | Local variable |
| `STORE_GLOBAL` | Module globals |
| `STORE_ATTR` | Object attribute |
| `STORE_DEREF` | Closure cell |

### Stack manipulation

| Opcode | Action |
|---|---|
| `POP_TOP` | Discard top of stack |
| `DUP_TOP` | Duplicate top of stack |
| `ROT_TWO` | Swap top two items |
| `ROT_THREE` | Rotate top three items |

### Control flow

| Opcode | Action |
|---|---|
| `JUMP_ABSOLUTE` | Unconditional jump |
| `POP_JUMP_IF_TRUE` | Conditional jump |
| `POP_JUMP_IF_FALSE` | Conditional jump |
| `FOR_ITER` | Get next from iterator or jump |
| `SETUP_FINALLY` | Set up try/except block |

---

## Comparing bytecode for performance insights

```python
# Which is faster: `x in set` or `x in list`?

def check_list(x):
    return x in [1, 2, 3, 4, 5]

def check_set(x):
    return x in {1, 2, 3, 4, 5}

dis.dis(check_list)
# BUILD_LIST ... → creates new list every call

dis.dis(check_set)
# LOAD_CONST (frozenset({1, 2, 3, 4, 5})) → constant, no build!
```

The CPython peephole optimizer converts `{1,2,3,4,5}` to a `frozenset` constant since it knows the set is used only for membership testing.

---

## .pyc files

Python caches compiled bytecode in `.pyc` files (in `__pycache__/`):

```python
import py_compile
import marshal
import struct

# Compile a file
py_compile.compile("example.py")
# Creates __pycache__/example.cpython-313.pyc

# Read a .pyc file
with open("__pycache__/example.cpython-313.pyc", "rb") as f:
    magic = f.read(4)       # magic number (identifies Python version)
    flags = f.read(4)       # PEP 552 flags
    timestamp = f.read(4)   # source modification time
    size = f.read(4)        # source file size
    code = marshal.load(f)  # the code object

print(type(code))           # <class 'code'>
print(code.co_consts)       # constants used in the module
```

---

## The instruction object API

```python
import dis

def example(x):
    if x > 0:
        return x * 2
    return -x

# Get structured instructions
for instr in dis.get_instructions(example):
    print(f"{instr.offset:4d} {instr.opname:<25} {instr.argrepr}")
```

Output:
```
   0 LOAD_FAST                 x
   2 LOAD_CONST                0
   4 COMPARE_OP               >
   6 POP_JUMP_IF_FALSE         14
   8 LOAD_FAST                 x
  10 LOAD_CONST                2
  12 BINARY_MULTIPLY           
  14 RETURN_VALUE              
  16 LOAD_FAST                 x
  18 UNARY_NEGATIVE            
  20 RETURN_VALUE              
```

Each `Instruction` object has:
```python
instr.opcode     # numeric opcode (int)
instr.opname     # human-readable name (str)
instr.arg        # numeric argument (int or None)
instr.argrepr    # human-readable argument (str)
instr.offset     # byte offset in co_code
instr.starts_line  # source line number (or None)
instr.is_jump_target  # True if another instruction jumps here
```

---

## Bytecode optimization examples

### Python's peephole optimizer

```python
# Constant folding
def f():
    return 2 * 3 * 4

dis.dis(f)
# LOAD_CONST  24   ← computed at compile time!
# RETURN_VALUE
```

```python
# Dead code elimination
def g():
    return 1
    print("unreachable")   # compiler may keep or remove this

dis.dis(g)
# LOAD_CONST  1
# RETURN_VALUE
# (the print may still be compiled but never reached)
```

---

## Modifying bytecode at runtime

```python
import types

def original():
    return 42

# Replace a constant in the code object
old_code = original.__code__
new_code = old_code.replace(co_consts=(None, 100))  # change 42 → 100

original.__code__ = new_code
print(original())   # 100
```

!!! warning "Dangerous"
    Bytecode modification can crash the interpreter if you produce invalid bytecode. The stack must always be balanced.

---

## The `opcode` module

```python
import opcode

# All opcodes
print(opcode.opname[:20])   # first 20 opcode names
print(opcode.HAVE_ARGUMENT)  # 90 — opcodes >= this have an argument

# Check if an opcode takes an argument
print(opcode.opname[124])    # 'LOAD_FAST'
print(124 >= opcode.HAVE_ARGUMENT)   # True — takes arg
```

---

## Practice Exercises

1. **Disassemble 5 different constructs** (for loop, while loop, try/except, list comprehension, generator expression) and explain each opcode.
2. **Write a function** that takes a function and returns the count of each opcode used.
3. **Compare the bytecode** of `sum(range(n))` vs a manual loop — explain why one is faster.
4. **Modify a function's constants** at runtime using `code.replace()` and verify the behavior changes.
5. **Write a bytecode analyzer** that detects functions with high stack depth (potential complexity).
6. **Read a `.pyc` file** manually with `marshal` and print all function names defined in it.
