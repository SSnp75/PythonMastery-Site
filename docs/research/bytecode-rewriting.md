---
title: Bytecode Rewriting
description: Inspecting and manipulating CPython bytecode — dis, code objects, runtime patching and instrumentation
---

# Bytecode Rewriting <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>🔬 Research Track · Level 7</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Open-ended</span>
    <span>📚 Prerequisite: <a href="../core/advanced/bytecode/">Bytecode</a></span>
  </div>
</div>

---

## Why rewrite bytecode?

- **Coverage tools** inject counting instructions at each line.
- **Profilers** trace function entry/exit.
- **Security sandboxes** block dangerous operations.
- **Optimizers** fold constants or remove dead code.
- **Instrumentation** adds logging without touching source.

CPython exposes enough of the compiled code object to inspect — and, carefully, modify — it.

---

## Inspecting bytecode with `dis`

```python
import dis

def add(a, b):
    return a + b

dis.dis(add)
#   2           0 RESUME                   0
#   3           2 LOAD_FAST                0 (a)
#               4 LOAD_FAST                1 (b)
#               6 BINARY_OP                0 (+)
#              10 RETURN_VALUE
```

Get the raw instruction list programmatically:

```python
import dis

def add(a, b):
    return a + b

ops = [i.opname for i in dis.get_instructions(add)]
print("BINARY_OP" in ops)   # True
```

---

## The code object

Every function carries a read-only `code` object describing its compiled form.

```python
def add(a, b):
    return a + b

code = add.__code__
print(code.co_argcount)    # 2
print(code.co_varnames)    # ('a', 'b')
print(code.co_consts)      # (None,)
print(type(code.co_code))  # <class 'bytes'>  (raw bytecode)
```

---

## Rewriting via `code.replace()`

Code objects are immutable, but `.replace()` returns a modified copy. Swapping a constant
changes what the function returns:

```python
def answer():
    return 41

code = answer.__code__
# co_consts holds (None, 41); bump 41 -> 42
new_consts = tuple(42 if c == 41 else c for c in code.co_consts)
answer.__code__ = code.replace(co_consts=new_consts)

print(answer())   # 42
```

!!! warning "Here be dragons"
    Hand-editing `co_code` risks a crash if offsets, the stack, or the line table get out of
    sync. For anything beyond swapping constants, use a library that maintains invariants.

---

## The `bytecode` library (safer surgery)

*Edit instructions with offsets recomputed for you, instead of hand-patching raw bytes.*

The third-party [`bytecode`](https://github.com/MatthieuDartiailh/bytecode) library gives an
editable instruction list that recomputes offsets for you:

```python
# pip install bytecode
from bytecode import Bytecode, Instr

def hello():
    return "hi"

bc = Bytecode.from_code(hello.__code__)
# Replace the loaded constant
for instr in bc:
    if isinstance(instr, Instr) and instr.name == "LOAD_CONST" and instr.arg == "hi":
        instr.arg = "HELLO"
hello.__code__ = bc.to_code()

print(hello())   # HELLO
```

---

## Practice exercises

1. Use `dis.get_instructions` to count how many `LOAD_FAST` ops a function uses.
2. Write a function that reports whether another function contains a loop (look for `FOR_ITER`).
3. Use `code.replace()` to change a function's name (`co_name`) and confirm via `__code__.co_name`.
4. Explore `dis.dis` output for a comprehension vs. an equivalent `for` loop.
