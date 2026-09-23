---
title: "Interpreter Forking"
description: Fork and modify CPython — custom builds, new opcodes and experimental runtimes
---

# Interpreter Forking <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>🔬 Research & Compilers</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 weeks</span>
    <span>📚 Prerequisites: <a href="../core/advanced/cpython-internals/">CPython Internals</a>, <a href="../core/advanced/bytecode/">Bytecode</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What forking the interpreter means and why people do it
- [x] The CPython source structure you'd touch
- [x] How new opcodes are added
- [x] Famous forks and experiments (GIL removal, subinterpreters)
- [x] Why this is a last resort

!!! note "This topic is about modifying CPython's C source"
    Forking the interpreter means editing and rebuilding CPython itself (C code). That can't be demonstrated with a runnable Python snippet, so this page is conceptual, referencing the real CPython source and documented build process. The `dis` example below (inspecting existing bytecode) *is* runnable and grounds the discussion.

---

## What "forking the interpreter" means

CPython — the reference Python implementation — is a C program that reads your bytecode and executes it. **Forking** it means taking that C source, changing how the language works at its core, and building your own `python` binary. This is the deepest level of language hacking: below your code, below the bytecode, into the machine that runs it.

People fork CPython to **experiment** with language features, performance ideas, or research questions that can't be expressed from within Python. Most forks are experiments; a few graduate into CPython itself.

```
   your .py  →  bytecode  →  [ CPython eval loop (C) ]  →  result
                              ▲
                              └── forking modifies THIS layer
```

## Seeing the layer you'd modify

You can inspect the bytecode the eval loop executes with `dis` — this is the interface between "your code" and "the interpreter's C". Runnable:

```python
import dis

def add(a, b):
    return a + b

dis.dis(add)
```

Output (abridged, version-dependent):

```text
  2   RESUME               0
  3   LOAD_FAST            a
      LOAD_FAST            b
      BINARY_OP            0 (+)
      RETURN_VALUE
```

Each line is an **opcode** the CPython eval loop handles in a giant C switch (historically in `ceval.c`). Forking the interpreter often means **adding or changing opcodes** in that loop. For example, adding a hypothetical `BINARY_POWER_MOD` opcode would mean: define it, emit it from the compiler, and handle it in the eval loop's C code.

---

## The CPython source you'd touch

A fork typically involves these parts of the CPython tree:

| Area | File(s) | Role |
|---|---|---|
| Grammar | `Grammar/python.gram` | Syntax rules (see [Grammar Modification](grammar-modification.md)) |
| AST definition | `Grammar/Python.asdl` | AST node types |
| Compiler | `Python/compile.c` | AST → bytecode |
| Opcodes | `Python/bytecodes.c` | The eval loop / opcode implementations |
| Objects | `Objects/*.c` | Built-in types (int, list, dict...) |

Adding a feature usually ripples through several of these: new syntax needs grammar + AST + compiler + eval loop changes, then a full rebuild.

---

## Famous forks and experiments

Interpreter forking has a rich history — and some experiments became hugely important:

- **No-GIL / free-threaded CPython (PEP 703)** — a long-running fork removing the Global Interpreter Lock, now being merged into CPython as an experimental build. Possibly the most consequential fork in Python's history.
- **Subinterpreters (PEP 554/734)** — multiple isolated interpreters in one process, developed partly as experimental branches before landing in the stdlib.
- **Cinder** (Meta) — a performance-oriented CPython fork with a JIT and other optimizations, running Instagram.
- **Pyston, Pyjion** — JIT-adding forks/experiments.
- **PyPy** — not a CPython fork but an entirely separate implementation with a tracing JIT (see the Performance section).

Many CPython performance wins (the "Faster CPython" project, specializing adaptive interpreter) were prototyped as experimental interpreter modifications before shipping.

---

## Why it's a last resort

!!! warning "Forking fragments the ecosystem"
    A forked interpreter runs code that standard Python can't, and standard tools may not understand your changes. Maintaining a fork means tracking upstream CPython forever. For almost everything, prefer C extensions, `importlib` import hooks ([Import System](../core/advanced/import-system.md)), or AST rewriting ([AST Manipulation](../core/advanced/ast-manipulation.md)) — they extend behavior without forking the language. Fork only for genuine language/runtime *research*, and ideally contribute findings back upstream rather than maintaining a permanent fork.

---

## Practice exercises

1. Use `dis` on several functions (a loop, a comprehension, a `with` block) and map each to the opcodes it produces.
2. Read the CPython source layout online and note which files you'd change to add a new built-in opcode.
3. Explain, in terms of the eval loop, why removing the GIL is so invasive (touches object refcounting everywhere).
4. Research one CPython fork (Cinder or the no-GIL build) and summarize what it changed and why.
5. Argue why an import-time AST transform is preferable to a fork for adding a custom behavior to your own project.
