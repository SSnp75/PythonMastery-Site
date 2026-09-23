---
title: "Python to MLIR"
description: Lower Python to MLIR — multi-level IR, dialects and modern compiler stacks
---

# Python → MLIR <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>🔬 Research & Compilers</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 weeks</span>
    <span>📚 Prerequisites: <a href="llvm-ir/">Python → LLVM IR</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What MLIR is and how it differs from LLVM IR
- [x] The idea of dialects and progressive lowering
- [x] Why ML compilers (JAX, PyTorch) use it
- [x] Where Python fits in the stack
- [x] The tradeoffs versus plain LLVM

!!! note "This is a conceptual/architectural topic"
    MLIR is a C++ compiler framework driven mostly through ML frameworks and specialized front-ends, not a `pip install` you script directly from Python. This page is conceptual — there's no runnable Python snippet that meaningfully demonstrates MLIR itself. It builds on the compilation concepts from [Python → LLVM IR](llvm-ir.md).

---

## What is MLIR?

**MLIR** (Multi-Level Intermediate Representation) is a newer compiler framework from the LLVM project, built to solve a problem LLVM IR alone doesn't: representing programs at **many levels of abstraction at once**. Where LLVM IR is a single low-level representation, MLIR lets a program be expressed — and gradually *lowered* — through multiple custom IRs called **dialects**.

```
   high-level ops (e.g. "matmul", "conv2d")     ← a domain dialect
        │  lower
        ▼
   loops + memory operations                     ← a mid-level dialect
        │  lower
        ▼
   LLVM IR dialect                                ← close to hardware
        │
        ▼
   machine code (CPU, GPU, TPU, accelerators)
```

Each step is a **dialect**, and compilation is **progressive lowering** from abstract to concrete. This is the key idea: instead of jumping straight from a high-level operation to low-level code, you descend through intermediate representations, optimizing at each level.

---

## Dialects: the core concept

A **dialect** is a self-contained set of operations and types for a particular domain or abstraction level. MLIR ships several and lets you define your own:

- A **tensor/linear-algebra dialect** can represent `matmul` as a single operation — perfect for optimizing whole ML computations.
- A **loop dialect** represents that same matmul as nested loops — the level where you tile and parallelize.
- The **LLVM dialect** is essentially LLVM IR inside MLIR — the final step before machine code.

Optimizations that are natural at a high level (fusing two matrix ops) are impossible once you've lowered to scalar loops — so keeping the high-level structure *and* being able to lower it is MLIR's superpower. This directly serves machine learning, where you want to optimize across whole tensor computation graphs.

---

## Why ML compilers use it

MLIR was born from the machine-learning world and underpins modern ML compiler stacks:

- **JAX / XLA** — compiles NumPy-like Python into optimized code for CPU/GPU/TPU; XLA's newer infrastructure uses MLIR. (See the Data & AI section's JAX topic.)
- **PyTorch** (torch-mlir, Inductor) — paths for compiling models via MLIR.
- **TensorFlow** — one of MLIR's original drivers.
- **Hardware vendors** — use MLIR to target accelerators (TPUs, NPUs) from the same high-level model.

The pattern: a Python front-end (JAX, PyTorch) captures your tensor computation as a graph, emits a high-level MLIR dialect, and the MLIR pipeline progressively lowers and optimizes it down to fast code for whatever hardware you're on.

---

## Where Python fits

You almost never write MLIR by hand from Python. Instead:

1. You write ordinary Python using a framework (JAX, PyTorch).
2. The framework **traces** your code into a computation graph.
3. It emits MLIR (a high-level dialect).
4. MLIR's passes lower and optimize it, ultimately reaching LLVM IR or hardware-specific code.

So "Python → MLIR" is really "Python framework → MLIR → hardware", with the framework doing the capture. This is why a JAX function decorated with `@jax.jit` can run fast on a TPU: under the hood it became MLIR, got optimized, and was compiled for that device.

---

## MLIR vs plain LLVM IR

| | **LLVM IR** | **MLIR** |
|---|---|---|
| Levels | One (low-level) | Many (dialects) |
| Abstraction | Fixed, scalar/pointer | Custom per domain (tensors, loops...) |
| Best for | Traditional languages (C, Rust) | Domain compilers, ML, accelerators |
| Extensibility | Limited | Define your own dialects |
| Relationship | — | Can lower *to* the LLVM dialect |

**The tradeoff:** MLIR's flexibility costs complexity — it's a heavier framework aimed at compiler engineers building domain-specific stacks. For compiling a conventional language, plain LLVM IR ([previous topic](llvm-ir.md)) is simpler. MLIR earns its keep when you have *domain structure worth preserving* (like tensor operations) across multiple lowering levels.

---

## Practice exercises

1. Explain "progressive lowering" in your own words, using matmul → loops → LLVM as the example.
2. Describe an optimization possible at a high-level tensor dialect that's impossible after lowering to scalar loops.
3. Research how JAX/XLA uses MLIR and summarize the Python-to-hardware path.
4. Contrast when you'd target plain LLVM IR versus MLIR for a new language or compiler.
5. Explain why hardware vendors favor MLIR for supporting new accelerators.
