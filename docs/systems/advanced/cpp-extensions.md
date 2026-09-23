---
title: "C++ Extensions"
description: Extend Python with C++ using pybind11 for native speed
---

# C++ Extensions <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="../../core/advanced/cpython-internals.md">CPython Internals</a>, C++ basics</span>
  </div>
</div>

---

## What you'll learn

- [x] Why write extensions in C++
- [x] pybind11 — the modern binding tool
- [x] Exposing functions and classes
- [x] Managing memory across the boundary
- [x] Build and packaging

When pure Python (even vectorized) isn't fast enough, you can write the hot part in **C++** and call it from Python. **pybind11** makes this remarkably clean. This complements the Rust path ([Rust Extensions](rust-extensions.md)).

!!! note "This topic requires a C++ toolchain"
    Building C++ extensions needs a compiler and pybind11, not present in this environment, so the code follows pybind11's documented API rather than being run-verified. The concepts and structure are what matter here.

---

## Why C++ extensions

Reasons to drop to C++:

- **Speed** — a tight numeric/algorithmic loop in C++ can be 10-100× faster than pure Python.
- **Existing C++ libraries** — wrap a mature C++ library to use it from Python.
- **Hardware/low-level access** — things Python can't do directly.

The pattern: **Python for the 95% (glue, I/O, orchestration), C++ for the 5% hot path.** You keep Python's productivity and get native speed where it counts.

---

## pybind11: the modern way

Historically, extensions used the raw CPython C API (verbose, error-prone) or SWIG. **pybind11** is a header-only C++ library that makes binding concise and safe. A function:

```cpp
// example.cpp
#include <pybind11/pybind11.h>

int add(int a, int b) {
    return a + b;
}

PYBIND11_MODULE(example, m) {
    m.doc() = "example module";
    m.def("add", &add, "Add two integers");
}
```

Then from Python:

```python
import example              # the compiled module
print(example.add(2, 3))    # -> 5, running in C++
```

That `PYBIND11_MODULE` macro and `m.def` are all it takes to expose a C++ function to Python — far less boilerplate than the raw C API.

---

## Exposing a C++ class

pybind11 maps C++ classes to Python classes naturally:

```cpp
#include <pybind11/pybind11.h>

class Accumulator {
public:
    Accumulator() : total_(0) {}
    void add(int x) { total_ += x; }
    int total() const { return total_; }
private:
    int total_;
};

PYBIND11_MODULE(example, m) {
    pybind11::class_<Accumulator>(m, "Accumulator")
        .def(pybind11::init<>())
        .def("add", &Accumulator::add)
        .def("total", &Accumulator::total);
}
```

```python
from example import Accumulator
acc = Accumulator()
acc.add(3); acc.add(4)
print(acc.total())     # -> 7
```

The C++ object behaves like a normal Python object. pybind11 also handles STL containers (`std::vector` ↔ `list`), and integrates with NumPy arrays for zero-copy numeric work.

---

## Memory & lifetime across the boundary

The trickiest part is object lifetime — who owns what:

- pybind11 manages Python's reference counting for you in common cases.
- **Return-value policies** control whether Python takes ownership of a returned C++ object, references it, or copies it — get this wrong and you get crashes or leaks.
- Passing large data (arrays) should be **zero-copy** where possible (pybind11 + NumPy buffer protocol) to avoid expensive copies across the boundary.

!!! warning "The boundary is where bugs live"
    Most C++-extension bugs are at the Python↔C++ boundary: ownership mistakes cause use-after-free crashes or leaks, and every crossing has a cost. Design a *coarse* interface — pass a big chunk of work across once, not millions of tiny calls. A chatty boundary erases the speed you gained.

---

## Build & packaging

You compile the C++ into a shared library Python can import:

- **setuptools + pybind11** — declare the extension in `pyproject.toml`/`setup.py`; `pip install` compiles it.
- **CMake + pybind11** — for larger C++ projects.
- **scikit-build-core** — modern bridge between CMake and Python packaging.

The built module is a `.so` (Linux/macOS) or `.pyd` (Windows) that imports like any Python module. Distributing means building wheels per platform (see [Packaging](../../web/competent/packaging.md)).

---

## C++ vs Rust vs Cython vs Numba

| Approach | Best when |
|---|---|
| **pybind11 (C++)** | You know C++ or need existing C++ libraries |
| **Rust ([Rust Extensions](rust-extensions.md))** | Want memory safety + speed; newer projects |
| **Cython** | Gradually typing Python for speed, less C++ needed |
| **Numba** | Numeric loops you can JIT with a decorator |

For a *new* speed-critical extension without an existing C++ codebase, many teams now reach for **Rust (PyO3)** for its safety. C++ (pybind11) shines when you already have C++ or need its ecosystem.

---

## Practice exercises

1. Explain when you'd write a C++ extension versus just vectorizing with NumPy.
2. Describe why a "chatty" fine-grained boundary can erase the speedup of native code.
3. Sketch the pybind11 binding for a function that takes and returns a list of numbers.
4. Explain what a return-value policy controls and why it matters for memory safety.
5. Compare pybind11 and PyO3 (Rust) for a new extension — what would drive your choice?
