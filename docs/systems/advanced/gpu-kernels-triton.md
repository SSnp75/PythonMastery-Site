---
title: "GPU Kernels (Triton)"
description: Write GPU kernels in Python with Triton for deep-learning speed
---

# GPU Kernels (Triton) <span class="pm-badge pm-badge-research">Advanced</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="vectorization.md">Vectorization</a>, GPU basics</span>
  </div>
</div>

---

## What you'll learn

- [x] Why GPUs are fast (and different)
- [x] What a GPU kernel is
- [x] Triton — writing kernels in Python
- [x] Where Triton fits (deep learning)
- [x] The mental model shift

GPUs run thousands of threads in parallel, making them ideal for the massively-parallel math in deep learning. **Triton** (from OpenAI) lets you write GPU **kernels in Python** instead of low-level CUDA C++.

!!! note "This topic requires a GPU + Triton"
    Triton compiles Python to GPU code and needs an NVIDIA GPU and the `triton` package — none present here. This page is conceptual, following Triton's documented model. There's no CPU-runnable equivalent, so nothing here is run-verified; treat it as an orientation to the ideas.

---

## Why GPUs are fast (and different)

A CPU has a few powerful cores optimized for sequential work. A GPU has *thousands* of simpler cores optimized for doing the **same operation on lots of data at once** (SIMT — single instruction, multiple threads).

```
   CPU:  a few fast cores       →  great for sequential, branchy code
   GPU:  thousands of cores     →  great for the SAME math over huge arrays
```

This is why GPUs dominate deep learning: training a neural network is billions of matrix multiplies — exactly the "same operation, tons of data" GPUs excel at. It's [vectorization](vectorization.md) taken to a massively parallel extreme.

---

## What a GPU kernel is

A **kernel** is a small function that runs on the GPU, executed simultaneously by many threads, each handling a piece of the data. Traditionally you write kernels in **CUDA C++** — powerful but low-level and hard: you manage thread indices, memory tiers (global/shared/registers), and synchronization by hand.

The challenge Triton addresses: CUDA is difficult and verbose, but the high-level frameworks (PyTorch) sometimes aren't fast enough for a custom operation. Triton is the middle ground.

---

## Triton: kernels in Python

Triton lets you write GPU kernels in a Python-like syntax; it compiles them to efficient GPU code, handling much of the low-level complexity (memory coalescing, tiling) automatically. A vector-add kernel, in Triton's documented style:

```python
import triton                      # pip install triton (needs NVIDIA GPU)
import triton.language as tl

@triton.jit
def add_kernel(x_ptr, y_ptr, out_ptr, n, BLOCK: tl.constexpr):
    pid = tl.program_id(0)                 # which block am I?
    offsets = pid * BLOCK + tl.arange(0, BLOCK)
    mask = offsets < n                     # don't read past the end
    x = tl.load(x_ptr + offsets, mask=mask)
    y = tl.load(y_ptr + offsets, mask=mask)
    tl.store(out_ptr + offsets, x + y, mask=mask)   # each thread adds its slice
```

Each program instance (block) handles a `BLOCK`-sized chunk of the arrays in parallel. Compared to CUDA C++, this is dramatically more approachable — you think in blocks and arrays, and Triton generates the fast GPU code. This is why Triton has become popular for writing custom deep-learning operations.

---

## Where Triton fits

Triton lives in the deep-learning performance world:

- **Custom operations** — when PyTorch's built-in ops don't fuse or optimize the way you need, write a Triton kernel.
- **Kernel fusion** — combine several operations into one GPU pass, avoiding slow round-trips to GPU memory.
- **PyTorch integration** — PyTorch's `torch.compile` uses Triton to generate optimized kernels automatically.
- **Research** — trying novel operations that don't exist in frameworks yet.

Most people benefit from Triton *indirectly* through `torch.compile`; writing kernels by hand is for when you need custom, maximally-fast operations.

---

## The mental model shift

Coming from CPU Python, GPU programming requires rethinking:

- **Think in thousands of threads**, not a loop — you write what *one* thread does to *its* piece, and thousands run at once.
- **Memory movement dominates** — getting data to/from the GPU and between its memory tiers is often the bottleneck, not the math. Minimizing data movement (fusion) is key.
- **Branches are costly** — divergent `if`s across threads hurt (threads run in lockstep groups).

!!! tip "Layered performance"
    The performance ladder: pure Python → [vectorized NumPy](vectorization.md) → JIT (Numba/PyPy) → C++/Rust extensions → **GPU kernels (Triton/CUDA)**. Each step is faster but more specialized. Reach for GPU kernels when you have massively parallel numeric work (deep learning) and the higher levels aren't enough. Most projects never need this rung — but it's where the frontier of ML performance lives.

---

## Practice exercises

1. Explain why a GPU suits matrix multiplication but not a branchy sequential algorithm.
2. In the vector-add kernel, explain what `mask = offsets < n` prevents.
3. Describe "kernel fusion" and why it reduces GPU memory traffic.
4. Explain how `torch.compile` lets you benefit from Triton without writing kernels.
5. Place Triton on the performance ladder and describe what problem justifies climbing to it.
