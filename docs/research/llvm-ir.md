---
title: "Python to LLVM IR"
description: Compile Python to LLVM IR for native-speed execution
---

# Python → LLVM IR <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>🔬 Research & Compilers</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 weeks</span>
    <span>📚 Prerequisites: <a href="../core/advanced/ast-manipulation/">AST Manipulation</a>, <a href="../core/advanced/bytecode/">Bytecode</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What LLVM and LLVM IR are
- [x] Why compiling Python to IR gives native speed
- [x] The compilation pipeline (AST → IR → machine code)
- [x] How `llvmlite` and Numba use this
- [x] The hard parts (Python's dynamism)

!!! note "This topic uses LLVM tooling not installed here"
    Generating LLVM IR from Python requires `llvmlite` (the binding used by Numba), which isn't installed in this environment, so the IR-generation snippets follow its documented API rather than being run-verified. The AST-inspection concepts they build on are covered and tested in [AST Manipulation](../core/advanced/ast-manipulation.md).

---

## What is LLVM IR?

**LLVM** is a compiler infrastructure that powers Clang (C/C++), Rust, Swift, and many others. Its heart is **LLVM IR** — an intermediate representation: a low-level, typed, assembly-like language that sits between your source code and the machine code for a specific CPU.

```
   Python AST  →  LLVM IR  →  optimizer passes  →  machine code (x86, ARM...)
   (high level)   (typed,      (LLVM's world-class   (native, fast)
                   portable)    optimizations)
```

The appeal: if you can translate Python (or a subset) into LLVM IR, you inherit LLVM's decades of optimization work and get **native-speed** execution — often 10-100x faster than the interpreter for numeric code. That's exactly what **Numba** does.

LLVM IR looks like this (a function returning `a + b`):

```llvm
define i64 @add(i64 %a, i64 %b) {
entry:
  %result = add i64 %a, %b
  ret i64 %result
}
```

Note it's **typed** (`i64` = 64-bit integer) and explicit — very different from dynamic Python.

---

## Generating IR from Python with `llvmlite`

`llvmlite` lets you build IR programmatically. The documented pattern for emitting that `add` function:

```python
from llvmlite import ir   # pip install llvmlite

# Types
int64 = ir.IntType(64)
fnty = ir.FunctionType(int64, (int64, int64))

# Module + function
module = ir.Module(name="demo")
func = ir.Function(module, fnty, name="add")
a, b = func.args

# Body
block = func.append_basic_block(name="entry")
builder = ir.IRBuilder(block)
result = builder.add(a, b)
builder.ret(result)

print(module)   # prints the LLVM IR text shown above
```

This constructs the IR in memory; a backend then compiles it to machine code you can call. `llvmlite` also provides the execution engine to JIT-compile and run it.

---

## The pipeline for compiling Python

A Python-to-LLVM compiler (like Numba's core) works roughly like this:

1. **Parse / get bytecode** — start from the function's AST or bytecode.
2. **Type inference** — figure out concrete types (LLVM IR requires them; Python doesn't declare them). This is the crux and the hard part.
3. **Lower to IR** — translate each operation into typed IR instructions.
4. **Optimize** — run LLVM's passes (inlining, vectorization, constant folding).
5. **Compile & run** — JIT to machine code, execute natively.

Numba does all this behind a decorator:

```python
from numba import njit   # pip install numba

@njit                     # compile to native code via LLVM on first call
def sum_squares(n):
    total = 0
    for i in range(n):
        total += i * i
    return total
```

The first call triggers type inference and LLVM compilation; subsequent calls run native machine code. See the Performance section's Numba topic for depth.

---

## The hard part: Python is dynamic

The reason you can't just compile *all* Python to fast IR:

- **Dynamic types.** `a + b` could be ints, floats, strings, lists, or custom objects — LLVM needs one concrete type. Compilers solve this only for code where types can be *inferred* (which is why Numba shines on numeric loops but can't accelerate arbitrary Python).
- **Dynamic dispatch, introspection, `eval`, monkey-patching** — Python's flexibility defeats ahead-of-time typing.
- **Objects everywhere.** A Python `int` is a heap object, not a machine register; getting native speed means using unboxed machine types, which only works when the compiler can prove it's safe.

This is why LLVM-based Python acceleration targets **numeric subsets** (Numba, and JAX via XLA) rather than the whole language.

---

## Practice exercises

1. Read the target IR for `add` above and identify the type annotations and the return instruction.
2. Explain why type inference is mandatory before lowering Python to LLVM IR.
3. Describe a Python function Numba can accelerate well, and one it can't — and why.
4. Compare this AOT/JIT-to-native approach with a bytecode interpreter's speed and flexibility tradeoff.
5. Research how Numba falls back ("object mode") when it can't infer types, and what that costs.
