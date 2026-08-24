---
title: NumPy
description: Arrays, broadcasting, vectorization, linear algebra and numerical computing
---

# NumPy <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>📊 Data & AI Track · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="../../core/beginner/data-structures/">Data Structures</a></span>
  </div>
</div>

---

## Why NumPy?

NumPy is 10-100x faster than Python lists for numerical operations because:

- Data is stored in **contiguous memory** (cache-friendly)
- Operations are implemented in **C** (no Python loop overhead)
- **Vectorized operations** process entire arrays at once

```python
import numpy as np
import time

# Python list — slow
py_list = list(range(1_000_000))
start = time.perf_counter()
result = [x**2 for x in py_list]
print(f"List: {time.perf_counter() - start:.4f}s")   # ~0.15s

# NumPy array — fast
arr = np.arange(1_000_000)
start = time.perf_counter()
result = arr**2
print(f"NumPy: {time.perf_counter() - start:.4f}s")  # ~0.002s (75x faster!)
```

---

## Creating arrays

```python
import numpy as np

# From Python sequences
a = np.array([1, 2, 3, 4, 5])
b = np.array([[1, 2, 3], [4, 5, 6]])   # 2D

# Typed
c = np.array([1, 2, 3], dtype=np.float64)
d = np.array([1, 2, 3], dtype=np.int32)

# Zeros, ones, empty
z = np.zeros((3, 4))          # 3x4 matrix of 0.0
o = np.ones((2, 3))           # 2x3 matrix of 1.0
e = np.empty((5,))            # uninitialized (fastest)
f = np.full((3, 3), 7)        # 3x3 matrix filled with 7

# Ranges
r1 = np.arange(0, 10, 0.5)   # like range() but supports floats
r2 = np.linspace(0, 1, 100)  # 100 evenly spaced points from 0 to 1
r3 = np.logspace(0, 3, 4)    # [1, 10, 100, 1000] (log-spaced)

# Identity and diagonal
eye = np.eye(4)               # 4x4 identity matrix
diag = np.diag([1, 2, 3])    # 3x3 diagonal matrix

# Random
rng = np.random.default_rng(42)   # modern random API
normal = rng.normal(0, 1, (3, 3))        # Gaussian(mean=0, std=1)
uniform = rng.uniform(0, 10, (2, 5))     # uniform [0, 10)
integers = rng.integers(0, 100, (4,))    # random ints
```

---

## Array properties

```python
a = np.array([[1, 2, 3], [4, 5, 6]])

print(a.shape)      # (2, 3)  — 2 rows, 3 columns
print(a.ndim)       # 2       — number of dimensions
print(a.size)       # 6       — total elements
print(a.dtype)      # int64   — data type
print(a.itemsize)   # 8       — bytes per element
print(a.nbytes)     # 48      — total bytes (6 * 8)
print(a.T)          # transposed view
```

---

## Indexing and slicing

```python
a = np.arange(20).reshape(4, 5)
# array([[ 0,  1,  2,  3,  4],
#        [ 5,  6,  7,  8,  9],
#        [10, 11, 12, 13, 14],
#        [15, 16, 17, 18, 19]])

# Basic
a[0, 0]        # 0  (element)
a[0]           # [0, 1, 2, 3, 4]  (first row)
a[:, 0]        # [0, 5, 10, 15]   (first column)
a[1:3, 2:4]   # [[7, 8], [12, 13]]  (sub-matrix)
a[::2, :]     # every other row

# Boolean indexing
mask = a > 10
print(a[mask])          # [11, 12, 13, 14, 15, 16, 17, 18, 19]
a[a % 2 == 0] = -1     # set all even elements to -1

# Fancy indexing (integer array indexing)
rows = np.array([0, 2, 3])
cols = np.array([1, 3, 4])
print(a[rows, cols])    # elements at (0,1), (2,3), (3,4)

# np.where — conditional selection
result = np.where(a > 10, a, 0)   # keep if > 10, else 0
```

---

## Vectorized operations

All arithmetic is element-wise by default:

```python
a = np.array([1, 2, 3, 4, 5])
b = np.array([10, 20, 30, 40, 50])

# Arithmetic
print(a + b)      # [11, 22, 33, 44, 55]
print(a * b)      # [10, 40, 90, 160, 250]
print(a ** 2)     # [1, 4, 9, 16, 25]
print(b / a)      # [10., 10., 10., 10., 10.]
print(b // a)     # [10, 10, 10, 10, 10]  (floor division)

# Comparison (returns boolean array)
print(a > 3)      # [False, False, False, True, True]
print(a == 3)     # [False, False, True, False, False]

# Universal functions (ufuncs)
print(np.sqrt(a))        # [1.0, 1.414, 1.732, 2.0, 2.236]
print(np.exp(a))         # [2.718, 7.389, 20.086, ...]
print(np.log(a))         # [0.0, 0.693, 1.099, 1.386, 1.609]
print(np.sin(a))         # sine of each element
print(np.abs(a - 3))     # [2, 1, 0, 1, 2]
print(np.maximum(a, 3))  # [3, 3, 3, 4, 5]
```

---

## Broadcasting

Broadcasting lets NumPy operate on arrays of different shapes by automatically expanding dimensions:

```python
# Scalar broadcast
a = np.array([[1, 2, 3], [4, 5, 6]])   # (2, 3)
print(a + 10)   # adds 10 to every element

# Row broadcast
row = np.array([100, 200, 300])   # (3,)
print(a + row)
# [[101, 202, 303],
#  [104, 205, 306]]

# Column broadcast
col = np.array([[10], [20]])   # (2, 1)
print(a + col)
# [[11, 12, 13],
#  [24, 25, 26]]

# Rules:
# 1. Compare dimensions from right to left
# 2. Dimensions are compatible if they're equal OR one of them is 1
# 3. Missing dimensions are treated as 1
```

### Broadcasting visualized:

```
a:   (2, 3)    → [[1, 2, 3], [4, 5, 6]]
row: (   3)    → [[100, 200, 300]]       ← broadcast over rows
Result: (2, 3) → [[101, 202, 303], [104, 205, 306]]

a:   (2, 3)    → [[1, 2, 3], [4, 5, 6]]
col: (2, 1)    → [[10], [20]]            ← broadcast over columns
Result: (2, 3) → [[11, 12, 13], [24, 25, 26]]
```

---

## Aggregation (reduction)

```python
a = np.array([[1, 2, 3], [4, 5, 6]])

# Global
print(a.sum())        # 21
print(a.mean())       # 3.5
print(a.std())        # 1.707
print(a.min())        # 1
print(a.max())        # 6
print(a.prod())       # 720

# Along an axis
print(a.sum(axis=0))  # [5, 7, 9]   — sum each column
print(a.sum(axis=1))  # [6, 15]     — sum each row
print(a.mean(axis=0)) # [2.5, 3.5, 4.5]

# Argmin/argmax — index of min/max
print(a.argmax())        # 5 (flat index)
print(a.argmax(axis=1))  # [2, 2] (column index of max in each row)

# Cumulative
print(np.cumsum(a.flatten()))   # [1, 3, 6, 10, 15, 21]
print(np.cumprod([1, 2, 3, 4]))  # [1, 2, 6, 24]
```

---

## Reshaping and stacking

```python
a = np.arange(12)

# Reshape
b = a.reshape(3, 4)     # 3x4 matrix
c = a.reshape(2, 2, 3)  # 3D array
d = a.reshape(-1, 3)    # auto-calculate first dim → (4, 3)

# Flatten
print(b.ravel())         # [0, 1, ..., 11]  (view — shares memory)
print(b.flatten())       # [0, 1, ..., 11]  (copy — own memory)

# Transpose
print(b.T)               # (4, 3) shape
print(b.transpose(1, 0)) # same as .T for 2D

# Stack
x = np.array([1, 2, 3])
y = np.array([4, 5, 6])
print(np.vstack([x, y]))    # [[1,2,3],[4,5,6]]  vertical
print(np.hstack([x, y]))    # [1,2,3,4,5,6]      horizontal
print(np.column_stack([x, y]))  # [[1,4],[2,5],[3,6]]

# Split
a = np.arange(16).reshape(4, 4)
top, bottom = np.vsplit(a, 2)     # split into 2 rows
left, right = np.hsplit(a, 2)     # split into 2 columns
```

---

## Linear Algebra

```python
# Matrix multiplication
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

print(A @ B)              # matrix multiply (Python 3.5+)
print(np.dot(A, B))       # same thing
# [[19, 22],
#  [43, 50]]

# NOT element-wise multiply:
print(A * B)              # [[5, 12], [21, 32]]  (element-wise!)

# Linear algebra operations
from numpy.linalg import inv, det, eig, svd, norm, solve

print(det(A))              # -2.0
print(inv(A))              # inverse matrix
print(norm(A))             # Frobenius norm

# Solve linear system: Ax = b
b = np.array([1, 2])
x = solve(A, b)           # x such that A @ x = b
print(x)                   # [-0., 0.5]

# Eigenvalues
eigenvalues, eigenvectors = eig(A)
print(eigenvalues)         # [-0.372, 5.372]

# SVD
U, S, Vt = svd(A)
```

---

## Performance tips

```python
# 1. Avoid Python loops — use vectorized operations
# BAD
result = np.zeros(1000000)
for i in range(1000000):
    result[i] = arr[i] ** 2

# GOOD
result = arr ** 2

# 2. Use views, not copies (when possible)
b = a[::2]     # view — no memory allocation
c = a[::2].copy()  # copy — allocates new memory

# 3. Pre-allocate output arrays
out = np.empty_like(a)
np.multiply(a, b, out=out)   # write directly to pre-allocated

# 4. Use appropriate dtypes
a = np.zeros(1000000, dtype=np.float32)   # 4 bytes vs 8 for float64

# 5. Check if you have a view or copy
print(b.base is a)   # True if b is a view of a
```

---

## Structured arrays (table-like data)

```python
dt = np.dtype([
    ("name", "U20"),
    ("age", "i4"),
    ("score", "f8"),
])

students = np.array([
    ("Alice", 30, 95.5),
    ("Bob", 25, 87.2),
    ("Charlie", 35, 92.1),
], dtype=dt)

print(students["name"])    # ['Alice', 'Bob', 'Charlie']
print(students["age"])     # [30, 25, 35]
print(students[students["score"] > 90])   # Alice and Charlie
```

---

## Practice Exercises

1. **Implement matrix multiplication** from scratch using loops, then compare speed with `@` operator.
2. **Solve a system of 3 linear equations** using `np.linalg.solve`.
3. **Compute the distance matrix** between N points in 2D using broadcasting (no loops).
4. **Implement a moving average** using slicing and vectorized operations.
5. **Write a function** that normalizes each column of a matrix to zero mean and unit variance.
6. **Simulate 10,000 dice rolls** and compute the distribution of sums of 3 dice.
7. **Implement k-means clustering** from scratch using only NumPy.
