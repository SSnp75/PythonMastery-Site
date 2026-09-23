---
title: "Sparse Tensors"
description: Store and compute on mostly-zero data efficiently
---

# Sparse Tensors <span class="pm-badge pm-badge-advanced">Scientific</span>

<div class="pm-topic-header">
  <strong>🔬 Scientific Computing</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prereqs: <a href="../data/intermediate/numpy.md">NumPy</a>, <a href="blas-lapack.md">BLAS & LAPACK</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What "sparse" means and why it matters
- [x] Build a sparse vector (tested)
- [x] Common sparse storage formats
- [x] The memory/speed tradeoff
- [x] SciPy sparse

Much real-world data is **mostly zeros** — a document's word counts (most words absent), a recommendation matrix (most users haven't rated most items), a graph's adjacency (most nodes not connected). Storing all those zeros wastes enormous memory. **Sparse** structures store only the nonzeros. The example here is **run-verified**.

---

## The idea: store only nonzeros (tested)

A dense vector of a million entries where only 3 are nonzero still uses a million slots. A sparse vector stores just the 3. Runnable:

```python
class SparseVector:
    def __init__(self, data: dict):
        # keep only nonzero entries
        self.data = {i: v for i, v in data.items() if v != 0}

    def dot(self, other: "SparseVector") -> float:
        # multiply only where BOTH are nonzero — the sparse win
        common = self.data.keys() & other.data.keys()
        return sum(self.data[k] * other.data[k] for k in common)

a = SparseVector({0: 1, 5: 2, 999: 3})     # conceptually a 1000-long vector
b = SparseVector({5: 4, 999: 1, 7: 9})

print("dot product:", a.dot(b))
print("entries stored in a:", len(a.data))
```

Output:

```text
dot product: 11
entries stored in a: 3
```

The dot product is `2×4 + 3×1 = 11` (only indices 5 and 999 overlap). Crucially, `a` stores **3 entries, not 1000** — and the dot product only iterates the nonzero overlap, not all 1000 positions. For real data with millions of dimensions and a handful of nonzeros each, this is the difference between feasible and impossible.

---

## Sparse storage formats

Different access patterns want different layouts. The common matrix formats:

| Format | Full name | Best for |
|---|---|---|
| **COO** | Coordinate list (row, col, value triples) | Building/constructing a matrix |
| **CSR** | Compressed Sparse Row | Fast row access, matrix-vector products |
| **CSC** | Compressed Sparse Column | Fast column access |
| **DOK** | Dictionary of Keys (like our example) | Incremental construction, random access |

You typically **build** in COO or DOK, then **convert** to CSR/CSC for computation. This build-then-optimize pattern mirrors how our `SparseVector` uses a dict (easy to build) but could convert to arrays for heavy math.

---

## The tradeoff

Sparse isn't always better:

- **Sparse wins** when the fraction of nonzeros (density) is low — say under ~10%. Huge memory savings and faster operations that skip zeros.
- **Dense wins** when data is fairly full — sparse formats have per-entry overhead (storing indices) and worse cache behavior. A 90%-full matrix is cheaper stored densely.

The crossover depends on the operation and hardware, but the rule of thumb: **use sparse when most entries are zero**, dense otherwise.

---

## In practice: SciPy sparse

For real work, **`scipy.sparse`** provides all the formats with optimized operations:

```python
from scipy.sparse import csr_matrix    # pip install scipy
import numpy as np

# Build from dense (or from COO triples)
dense = np.array([[0, 0, 3], [4, 0, 0], [0, 0, 0]])
sparse = csr_matrix(dense)

print(sparse.nnz)          # 2 — number of stored nonzeros
result = sparse @ sparse.T # sparse matrix multiply
```

!!! note "SciPy snippet follows documented API"
    SciPy isn't installed here (the `SparseVector` above is run-verified). `scipy.sparse` handles the formats, conversions, and fast operations. It's essential for large-scale linear algebra, graph algorithms, and NLP (term-document matrices), where dense storage would blow past memory limits.

---

## Where sparse data appears

- **NLP** — term-document matrices (vocabulary is huge, each document uses few words).
- **Recommendation systems** — user×item rating matrices (mostly unrated).
- **Graphs** — adjacency matrices (most pairs unconnected); see the Algorithms section.
- **Finite element / PDE solvers** — the matrices in [Computational Physics](computational-physics.md) are often sparse.
- **Machine learning** — one-hot encoded features, sparse gradients.

---

## Practice exercises

1. Add a `norm()` method to `SparseVector` (sqrt of dot with itself).
2. Add sparse vector addition (union of keys, summing overlaps).
3. Explain the memory difference between dense and sparse storage for a vector of length 1,000,000 with 5 nonzeros.
4. Represent a small graph as a sparse adjacency structure and check if an edge exists.
5. Estimate the density below which sparse beats dense for your use case, and why cache behavior matters.
