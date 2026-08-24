---
title: Rust Extensions
description: PyO3, maturin, memory safety, GIL management and high-performance Python extensions
---

# Rust Extensions <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance Track · Level 5</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 weeks</span>
    <span>📚 Prerequisites: <a href="profiling/">Profiling</a>, Rust basics</span>
  </div>
</div>

---

## Why Rust for Python extensions?

| Advantage | Explanation |
|---|---|
| Memory safety | No segfaults, no buffer overflows (compile-time guarantees) |
| No GC | Predictable performance, no pause spikes |
| C-level speed | Compiled to native code via LLVM |
| Great tooling | cargo, clippy, rustfmt — modern dev experience |
| Easy Python bindings | PyO3 makes it seamless |
| Thread-safe | Ownership model prevents data races |

---

## Quick start with maturin

```bash
# Install tools
pip install maturin
cargo install cargo-expand   # optional: inspect macro expansions

# Create project
mkdir my_rust_module && cd my_rust_module
maturin init --bindings pyo3

# Project structure:
# my_rust_module/
# ├── Cargo.toml
# ├── pyproject.toml
# └── src/
#     └── lib.rs
```

### Cargo.toml

```toml
[package]
name = "my_rust_module"
version = "0.1.0"
edition = "2021"

[lib]
name = "my_rust_module"
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.22", features = ["extension-module"] }
numpy = "0.22"   # for NumPy integration
```

---

## Basic functions

```rust
// src/lib.rs
use pyo3::prelude::*;

/// Compute the sum of squares (10-100x faster than Python)
#[pyfunction]
fn sum_of_squares(n: u64) -> u64 {
    (1..=n).map(|i| i * i).sum()
}

/// Fibonacci with memoization
#[pyfunction]
fn fibonacci(n: u64) -> u64 {
    let mut a: u64 = 0;
    let mut b: u64 = 1;
    for _ in 0..n {
        let tmp = a + b;
        a = b;
        b = tmp;
    }
    a
}

/// String processing
#[pyfunction]
fn count_vowels(s: &str) -> usize {
    s.chars()
        .filter(|c| "aeiouAEIOU".contains(*c))
        .count()
}

/// Register all functions in the module
#[pymodule]
fn my_rust_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_of_squares, m)?)?;
    m.add_function(wrap_pyfunction!(fibonacci, m)?)?;
    m.add_function(wrap_pyfunction!(count_vowels, m)?)?;
    Ok(())
}
```

### Build and use:

```bash
maturin develop   # builds and installs in current venv
```

```python
import my_rust_module

print(my_rust_module.sum_of_squares(1_000_000))  # instant!
print(my_rust_module.fibonacci(50))               # 12586269025
print(my_rust_module.count_vowels("Hello World")) # 3
```

---

## Python classes in Rust

```rust
use pyo3::prelude::*;

#[pyclass]
struct Point {
    #[pyo3(get, set)]
    x: f64,
    #[pyo3(get, set)]
    y: f64,
}

#[pymethods]
impl Point {
    #[new]
    fn new(x: f64, y: f64) -> Self {
        Point { x, y }
    }

    fn distance(&self, other: &Point) -> f64 {
        ((self.x - other.x).powi(2) + (self.y - other.y).powi(2)).sqrt()
    }

    fn __repr__(&self) -> String {
        format!("Point({}, {})", self.x, self.y)
    }

    fn __add__(&self, other: &Point) -> Point {
        Point {
            x: self.x + other.x,
            y: self.y + other.y,
        }
    }
}
```

```python
from my_rust_module import Point

p1 = Point(3.0, 4.0)
p2 = Point(6.0, 8.0)
print(p1.distance(p2))   # 5.0
print(p1 + p2)           # Point(9.0, 12.0)
print(p1.x, p1.y)        # 3.0 4.0
```

---

## NumPy integration

```rust
use numpy::{IntoPyArray, PyArrayDyn, PyReadonlyArrayDyn};
use pyo3::prelude::*;
use ndarray::ArrayD;

#[pyfunction]
fn double_array<'py>(
    py: Python<'py>,
    arr: PyReadonlyArrayDyn<'py, f64>,
) -> Bound<'py, PyArrayDyn<f64>> {
    let input = arr.as_array();
    let output: ArrayD<f64> = &input * 2.0;
    output.into_pyarray_bound(py)
}

#[pyfunction]
fn element_wise_sqrt<'py>(
    py: Python<'py>,
    arr: PyReadonlyArrayDyn<'py, f64>,
) -> Bound<'py, PyArrayDyn<f64>> {
    let input = arr.as_array();
    let output = input.mapv(|x| x.sqrt());
    output.into_pyarray_bound(py)
}
```

```python
import numpy as np
from my_rust_module import double_array, element_wise_sqrt

arr = np.array([1.0, 4.0, 9.0, 16.0])
print(double_array(arr))         # [2., 8., 18., 32.]
print(element_wise_sqrt(arr))    # [1., 2., 3., 4.]
```

---

## Releasing the GIL

```rust
use pyo3::prelude::*;

#[pyfunction]
fn cpu_intensive(py: Python<'_>, n: u64) -> u64 {
    // Release the GIL — other Python threads can run!
    py.allow_threads(|| {
        // Pure Rust computation — no Python objects allowed here
        (1..=n).map(|i| i * i).sum()
    })
}
```

This means Python threads can run concurrently while Rust does heavy computation.

---

## Error handling

```rust
use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;

#[pyfunction]
fn divide(a: f64, b: f64) -> PyResult<f64> {
    if b == 0.0 {
        Err(PyValueError::new_err("Division by zero"))
    } else {
        Ok(a / b)
    }
}
```

```python
from my_rust_module import divide

print(divide(10.0, 3.0))   # 3.333...

try:
    divide(1.0, 0.0)
except ValueError as e:
    print(e)   # Division by zero
```

---

## Async Rust functions

```rust
use pyo3::prelude::*;
use pyo3_asyncio_0_21::tokio::future_into_py;

#[pyfunction]
fn async_fetch(py: Python<'_>, url: String) -> PyResult<Bound<'_, PyAny>> {
    future_into_py(py, async move {
        let body = reqwest::get(&url)
            .await
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?
            .text()
            .await
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
        Ok(body)
    })
}
```

---

## Performance comparison

```python
import timeit
import my_rust_module

# Fibonacci benchmark
print("Python:", timeit.timeit("fib_py(30)", globals=globals(), number=100000))
print("Rust:  ", timeit.timeit("my_rust_module.fibonacci(30)", globals=globals(), number=100000))
# Python: ~4.5s
# Rust:   ~0.03s  (150x faster)
```

---

## Publishing to PyPI

```bash
# Build wheels for all platforms
maturin build --release

# Or publish directly
maturin publish   # uploads to PyPI

# CI/CD — use maturin-action in GitHub Actions
```

---

## Practice Exercises

1. **Write a Rust function** that finds all prime numbers below N using a sieve.
2. **Create a Rust class** with Python-accessible methods and properties.
3. **Process a NumPy array** in Rust — normalize (zero mean, unit std) each column.
4. **Release the GIL** in a CPU-heavy function and verify Python threads run concurrently.
5. **Benchmark** the same algorithm in Python, Cython, Numba and Rust — compare speeds.
6. **Publish** your Rust extension to TestPyPI with maturin.
