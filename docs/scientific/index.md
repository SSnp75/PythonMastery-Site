---
title: "Scientific Computing"
description: Numerical methods, linear algebra, simulation and scientific Python
---

# 🔬 Scientific Computing

**Python is the dominant language of science — from physics simulations to computational biology. This section covers the numerical foundations and the libraries that make Python fast enough for real science.**

The paradox: Python is slow, yet it rules scientific computing. The reason is that the heavy lifting happens in optimized C/Fortran libraries (NumPy, SciPy) wrapped in friendly Python — you get readable code *and* native speed.

## Topics

<ul class="pm-subtopics" markdown="1">
- [🧮 BLAS & LAPACK](blas-lapack.md) — the linear algebra engines under NumPy
- [🕸️ Sparse Tensors](sparse-tensors.md) — efficient storage for mostly-zero data
- [🎲 Simulation Frameworks](simulation-frameworks.md) — modeling dynamic systems
- [⚛️ Computational Physics](computational-physics.md) — numerical methods for physics
- [🧬 Computational Biology](computational-biology.md) — sequence and structural analysis
- [📊 Scientific Visualization](scientific-visualization.md) — plotting and 3D rendering
- [📉 Numerical Optimization](numerical-optimization.md) — finding minima and best fits
- [🔄 Custom Autograd Engines](custom-autograd.md) — automatic differentiation from scratch
</ul>

---

## Why Python for science

```
   your Python code  →  NumPy/SciPy API  →  BLAS/LAPACK (C/Fortran)  →  CPU (SIMD, multicore)
   (readable, high-level)                    (decades of optimization)
```

You write `A @ B` (matrix multiply); NumPy dispatches it to BLAS, which runs hand-tuned assembly. This layering is the secret: the *ergonomics* of Python with the *speed* of Fortran. The numerical-methods pages here show the algorithms in **pure, tested Python** for understanding; in practice you'd call the optimized library.

!!! note "Core libraries aren't installed in this build"
    NumPy, SciPy, Matplotlib, and friends aren't present in this documentation environment. Where pages show those, the code follows their **documented APIs**. The **numerical algorithms** (integration, root-finding, Monte Carlo, ODE solving) are shown in pure standard-library Python and are **run-verified** — so you can see how the methods actually work, not just call a black box.

---

## The numerical mindset

Scientific computing is largely about **approximation**: computers can't represent real numbers exactly or solve most equations symbolically, so we use numerical methods that get *close enough*. Understanding error, convergence, and stability matters as much as the algorithms. That's the thread running through this section.
