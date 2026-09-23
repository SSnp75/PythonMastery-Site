---
title: "BLAS & LAPACK"
description: The linear algebra engines that make NumPy fast
---

# BLAS & LAPACK <span class="pm-badge pm-badge-advanced">Scientific</span>

<div class="pm-topic-header">
  <strong>🔬 Scientific Computing</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prereqs: <a href="../data/intermediate/numpy.md">NumPy</a>, linear algebra basics</span>
  </div>
</div>

---

## What you'll learn

- [x] What BLAS and LAPACK are
- [x] Why they make NumPy fast
- [x] The three BLAS levels
- [x] Naive vs library matrix multiply (tested naive version)
- [x] How this shapes performance

Behind NumPy's speed sit two venerable Fortran/C libraries: **BLAS** and **LAPACK**. Understanding them explains *why* `A @ B` in NumPy is thousands of times faster than a Python loop.

---

## What they are

- **BLAS** (Basic Linear Algebra Subprograms) — low-level routines for vector and matrix operations: dot products, matrix-vector, matrix-matrix multiply. Decades of hand-tuned optimization.
- **LAPACK** (Linear Algebra PACKage) — higher-level routines built *on* BLAS: solving linear systems, eigenvalues, decompositions (LU, QR, SVD).

```
   NumPy / SciPy  (Python API)
        │  calls
        ▼
   LAPACK   (solvers, decompositions)
        │  built on
        ▼
   BLAS     (multiply, dot — hand-tuned assembly)
        │
        ▼
   CPU      (SIMD vector instructions, cache-optimized, multithreaded)
```

When you call `numpy.linalg.solve` or `A @ B`, you're really invoking optimized BLAS/LAPACK code — often an implementation like OpenBLAS, Intel MKL, or Apple Accelerate, tuned for your exact CPU.

---

## Why it's fast: naive vs optimized

Here's a naive matrix multiply in pure Python — correct but slow. Runnable:

```python
def matmul(A, B):
    n, m, p = len(A), len(B), len(B[0])
    result = [[0] * p for _ in range(n)]
    for i in range(n):
        for k in range(m):
            aik = A[i][k]
            for j in range(p):
                result[i][j] += aik * B[k][j]
    return result

A = [[1, 2], [3, 4]]
B = [[5, 6], [7, 8]]
print(matmul(A, B))
```

Output:

```text
[[19, 22], [43, 50]]
```

The math is right (`[[1·5+2·7, 1·6+2·8], ...]`), but this triple loop is orders of magnitude slower than BLAS for large matrices. **Why BLAS crushes it:**

- **SIMD** — one CPU instruction multiplies several numbers at once.
- **Cache blocking** — data is processed in chunks that fit in fast CPU cache, avoiding slow memory trips.
- **Multithreading** — work spread across cores.
- **Hand-tuned assembly** — decades of optimization for specific chips.

You will never beat BLAS with Python loops. The lesson: **express math as array operations** so NumPy dispatches to BLAS, rather than looping in Python (see [Vectorization](../systems/advanced/vectorization.md)).

---

## The three BLAS levels

BLAS routines are grouped by how much work they do per unit of data — which determines how well they use the hardware:

| Level | Operation | Example | Performance |
|---|---|---|---|
| **1** | vector-vector | dot product, `y = ax + y` | Memory-bound (little reuse) |
| **2** | matrix-vector | `y = Ax` | Moderate |
| **3** | matrix-matrix | `C = AB` | Compute-bound — best hardware use |

**Level 3 (matrix-matrix) is the sweet spot**: it does O(n³) work on O(n²) data, so each value loaded from memory gets reused many times, keeping the CPU busy. This is why algorithms are often reformulated to use matrix-matrix products — it's the operation hardware runs most efficiently.

---

## LAPACK: the higher-level solvers

LAPACK provides what you actually call for real problems:

```python
import numpy as np                 # pip install numpy

A = np.array([[3, 1], [1, 2]])
b = np.array([9, 8])

x = np.linalg.solve(A, b)          # solve Ax = b (LAPACK under the hood)
eigenvalues = np.linalg.eigvals(A) # eigenvalues (LAPACK)
U, S, Vt = np.linalg.svd(A)        # singular value decomposition (LAPACK)
```

!!! note "NumPy snippet follows documented API"
    NumPy isn't installed here, so this isn't run-verified (the naive matmul is). Each of these calls dispatches to LAPACK routines that are numerically careful and fast — reimplementing an SVD or a stable linear solver by hand is a research project in itself. Use the library.

---

## Practice exercises

1. Time the naive `matmul` on growing matrix sizes and observe the O(n³) growth.
2. Explain why a Level-3 (matrix-matrix) operation uses hardware better than Level-1 (vector).
3. Describe what happens under the hood when you write `A @ B` in NumPy.
4. Look up which BLAS implementation your NumPy uses (`np.show_config()`) — MKL, OpenBLAS, etc.
5. Explain why "vectorize, don't loop" is the golden rule of NumPy performance.
