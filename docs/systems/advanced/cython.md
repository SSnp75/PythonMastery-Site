---
title: Cython
description: Static types, .pyx files, typed memoryviews, wrapping C libraries and compilation
---

# Cython <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance Track · Level 5</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 weeks</span>
    <span>📚 Prerequisites: <a href="profiling/">Profiling</a>, C basics</span>
  </div>
</div>

---

## What is Cython?

Cython is a **superset of Python** that compiles to C. Adding type annotations gives C-level speed while keeping Python-like syntax.

```
Python code (slow) → Add Cython types → Compile to C → C-speed extension
```

Typical speedup: **10x–100x** for numerical loops.

---

## Setup

```bash
pip install cython setuptools
```

```python
# setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("my_module.pyx", annotate=True),
)
```

```bash
python setup.py build_ext --inplace
# Creates my_module.c and my_module.cpython-313-*.so
```

---

## Basic Cython — adding types

```cython
# fib.pyx
def fib_python(n):
    """Pure Python — baseline."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def fib_cython(int n):
    """Cython with typed variables — 50-100x faster."""
    cdef long long a = 0, b = 1
    cdef int i
    for i in range(n):
        a, b = b, a + b
    return a
```

```python
# Benchmark
import timeit
from fib import fib_python, fib_cython

print(timeit.timeit("fib_python(1000)", globals=globals(), number=10000))   # ~3.5s
print(timeit.timeit("fib_cython(1000)", globals=globals(), number=10000))   # ~0.05s
# 70x speedup!
```

---

## Type declarations

```cython
# Variable types
cdef int x = 10
cdef double y = 3.14
cdef long long big_num = 10**18
cdef bint flag = True          # C boolean (0 or 1)

# Function types
cdef int add(int a, int b):    # C function — not callable from Python
    return a + b

cpdef int add_public(int a, int b):   # callable from both C and Python
    return a + b

def add_python(int a, int b):  # Python function with typed args
    return a + b
```

| Keyword | Callable from Python? | Callable from Cython? | Speed |
|---|---|---|---|
| `def` | Yes | Yes | Python speed (unless typed args) |
| `cdef` | No | Yes | C speed |
| `cpdef` | Yes | Yes | C speed (with Python wrapper) |

---

## Typed memoryviews (fast array access)

```cython
# primes.pyx
import numpy as np
cimport numpy as cnp

def find_primes(int limit):
    """Sieve of Eratosthenes — fast with typed memoryview."""
    cdef cnp.uint8_t[:] is_prime = np.ones(limit + 1, dtype=np.uint8)
    cdef int i, j

    is_prime[0] = 0
    is_prime[1] = 0

    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = 0

    return [i for i in range(limit + 1) if is_prime[i]]
```

### Memoryview vs NumPy indexing:

```cython
# SLOW — Python object indexing
def slow(numpy_array):
    cdef int i
    s = 0
    for i in range(len(numpy_array)):
        s += numpy_array[i]    # Python __getitem__ each time!
    return s

# FAST — typed memoryview (direct memory access)
def fast(double[:] arr):
    cdef int i
    cdef double s = 0
    for i in range(arr.shape[0]):
        s += arr[i]            # direct C pointer arithmetic!
    return s
```

---

## Parallel loops with prange

```cython
# parallel.pyx
from cython.parallel import prange
import numpy as np

def compute_parallel(double[:] data, int n):
    """Parallel computation — releases GIL!"""
    cdef int i
    cdef double[:] result = np.empty(n)

    # nogil + prange = true parallel execution
    with nogil:
        for i in prange(n):
            result[i] = data[i] ** 2 + data[i] * 3.14

    return np.asarray(result)
```

Compile with OpenMP:
```python
# setup.py
from setuptools import setup, Extension
from Cython.Build import cythonize

ext = Extension(
    "parallel",
    sources=["parallel.pyx"],
    extra_compile_args=["-fopenmp"],
    extra_link_args=["-fopenmp"],
)
setup(ext_modules=cythonize([ext]))
```

---

## Wrapping C libraries

```cython
# wrapper.pyx

# Declare the C function
cdef extern from "math.h":
    double sin(double x)
    double cos(double x)
    double sqrt(double x)

# Python-accessible wrapper
def py_sin(double x):
    return sin(x)

# Wrap a custom C library
cdef extern from "mylib.h":
    int fast_hash(const char* data, int length)
    void process_buffer(double* buf, int size)

def hash_string(str s):
    cdef bytes encoded = s.encode('utf-8')
    return fast_hash(encoded, len(encoded))
```

---

## The annotation report

```bash
cython -a my_module.pyx   # generates my_module.html
```

The HTML shows each line colored:
- **White** → pure C (fast)
- **Yellow** → Python interaction (slow)

Goal: make hot loops white (no yellow lines).

---

## When to use Cython vs alternatives

| Tool | Best for | Effort | Speedup |
|---|---|---|---|
| **Cython** | Existing Python code, wrapping C | Medium | 10-100x |
| **Numba** | NumPy-heavy numerical code | Low | 10-100x |
| **PyO3 (Rust)** | New high-perf modules | High | 50-200x |
| **ctypes/cffi** | Calling existing C libraries | Low | Depends |
| **NumPy vectorization** | Array operations | Very low | 5-50x |

---

## Practice Exercises

1. **Cythonize a numerical function** and measure the speedup vs pure Python.
2. **Use typed memoryviews** to speed up element-wise operations on large arrays.
3. **Wrap a C library** (e.g., zlib compression) with Cython.
4. **Use prange** for a parallel computation and verify it uses multiple cores.
5. **Read the annotation report** and eliminate all yellow lines from a function.
6. **Compare** Cython vs Numba vs pure NumPy for the same computation.
