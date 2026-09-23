---
title: "PyPy"
description: An alternative Python with a JIT compiler for big speedups
---

# PyPy <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 days</span>
    <span>📚 Prerequisites: <a href="profiling.md">Profiling</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What PyPy is and how it differs from CPython
- [x] How its JIT makes code fast
- [x] When PyPy helps (and when it doesn't)
- [x] Compatibility considerations

**PyPy** is an alternative Python implementation with a **tracing JIT compiler** that can run pure-Python code many times faster than CPython — often 4-10× on suitable workloads, with no code changes.

!!! note "PyPy is a separate interpreter"
    PyPy is a different `python` binary, not a library. It can't be demonstrated with a snippet in this CPython environment — this page is conceptual. You'd install PyPy separately and run `pypy your_script.py` instead of `python your_script.py`.

---

## CPython vs PyPy

- **CPython** — the reference implementation (what you normally run). Interprets bytecode; simple and universally compatible, but the interpreter loop has overhead.
- **PyPy** — implements the same Python language but adds a **Just-In-Time compiler**. It runs your code, notices hot loops, and compiles them to machine code on the fly.

```
   CPython:  bytecode ──interpreted every time──▶ result
   PyPy:     bytecode ──interpret, detect hot loop, JIT to machine code──▶ fast result
```

Both run the *same* Python source. PyPy is a drop-in alternative for most pure-Python programs.

---

## How the tracing JIT works

PyPy's JIT is a **tracing** JIT:

1. Run the program interpreted, counting how often loops execute.
2. When a loop is "hot" (runs many times), **trace** one iteration — record the exact operations performed.
3. Compile that trace to optimized machine code, with **guards** that check the assumptions still hold (e.g. the types haven't changed).
4. Run the fast machine code; if a guard fails (an assumption broke), fall back to the interpreter.

This is why PyPy excels at **long-running, loop-heavy** pure-Python code — there's a hot loop to trace and specialize. (See [Custom JIT Compilers](../../research/jit.md) for the general idea.)

---

## When PyPy helps

**Great fit:**
- Long-running, CPU-bound, pure-Python programs with hot loops (simulations, interpreters, algorithmic code).
- Code that spends its time *in Python*, not in C libraries.

**Poor fit / no benefit:**
- Short scripts — the JIT needs warm-up time to pay off; a quick script finishes before it helps.
- Code dominated by C extensions (NumPy-heavy work) — the time is already in optimized C, so PyPy's JIT has little Python to speed up, and C-extension compatibility can be a problem.
- I/O-bound programs — the bottleneck is waiting, not computing.

---

## Compatibility

PyPy aims for high CPython compatibility and runs most pure-Python code unchanged. The main friction:

- **C extensions** — PyPy supports the CPython C API via a compatibility layer (`cpyext`), but it's slower there and some extensions don't work or need PyPy-specific versions. NumPy works but doesn't get PyPy's JIT benefit.
- **Version lag** — PyPy usually targets a slightly older Python version than the latest CPython.
- **Memory** — PyPy can use more memory (a JIT and different GC).

!!! tip "How to decide"
    Profile on CPython first ([Profiling](profiling.md)). If your bottleneck is **pure-Python computation in hot loops** (not C libraries, not I/O), try running the same code on PyPy — it may be several times faster with zero changes. If the time is in NumPy/C or I/O, PyPy won't help; look at [Vectorization](vectorization.md), Cython, or async instead. Also weigh the "Faster CPython" gains ([Runtime Evolution](../../emerging/runtime-evolution.md)), which narrow the gap.

---

## Practice exercises

1. Explain, in terms of the tracing JIT, why PyPy speeds up a long loop but not a short script.
2. Describe a workload where PyPy would give a big win and one where it would give none.
3. Explain why NumPy-heavy code doesn't benefit much from PyPy.
4. Research PyPy's current CPython version compatibility and note one limitation.
5. Compare the PyPy JIT approach to CPython's newer specializing adaptive interpreter.
