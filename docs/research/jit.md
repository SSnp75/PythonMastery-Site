---
title: Custom JIT Compilers
description: Tracing JIT design, type specialization, guard insertion and LLVM backend
---

# Custom JIT Compilers <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>🔬 Research Track · Level 7</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Open-ended</span>
    <span>📚 Prerequisites: <a href="../core/advanced/bytecode/">Bytecode</a>, <a href="../core/advanced/cpython-internals/">CPython Internals</a></span>
  </div>
</div>

---

## What is a JIT compiler?

A JIT (Just-In-Time) compiler translates bytecode to native machine code **at runtime**, specializing for the actual types and values observed.

```
Interpreter (slow, general):   bytecode → interpret each instruction
JIT (fast, specialized):       bytecode → observe types → compile native code → execute
```

---

## Tracing JIT — the core concept

A tracing JIT records the **hot path** (frequently executed code), compiles it, and inserts **guards** for assumptions:

```python
# Simplified tracing JIT concept

class Trace:
    """A recorded sequence of operations with type guards."""
    def __init__(self):
        self.operations = []
        self.guards = []

    def record_op(self, op, *args):
        self.operations.append((op, args))

    def add_guard(self, variable, expected_type):
        self.guards.append((variable, expected_type))

class TracingJIT:
    def __init__(self):
        self.traces = {}      # function → compiled trace
        self.call_counts = {} # function → count (detect hot functions)
        self.threshold = 100  # compile after N calls

    def should_compile(self, func_name):
        self.call_counts[func_name] = self.call_counts.get(func_name, 0) + 1
        return self.call_counts[func_name] >= self.threshold

    def record_trace(self, func, args):
        """Record one execution to build a trace."""
        trace = Trace()

        # Observe argument types
        for i, arg in enumerate(args):
            trace.add_guard(f"arg_{i}", type(arg))

        # Record operations (simplified — real JIT traces bytecodes)
        # In practice: instrument the interpreter to emit trace entries
        trace.record_op("LOAD_ARG", 0)
        trace.record_op("LOAD_ARG", 1)
        trace.record_op("BINARY_ADD")
        trace.record_op("RETURN")

        return trace

    def compile_trace(self, trace: Trace):
        """Compile trace to native code (via LLVM in real JIT)."""
        # In reality: emit LLVM IR, optimize, generate machine code
        print(f"  Compiled trace: {len(trace.operations)} ops, "
              f"{len(trace.guards)} guards")
        # Return a callable that executes the compiled code
        return lambda *args: None   # placeholder

    def execute(self, func, *args):
        name = func.__name__
        if name in self.traces:
            # Check guards
            compiled = self.traces[name]
            return compiled(*args)
        elif self.should_compile(name):
            trace = self.record_trace(func, args)
            self.traces[name] = self.compile_trace(trace)
            return self.traces[name](*args)
        else:
            return func(*args)   # interpret normally
```

---

## Type specialization

The key optimization: generate different code for different types.

```python
# Python's + operator is polymorphic:
# int + int    → uses C integer addition
# str + str    → uses string concatenation
# list + list  → uses list extend
# obj + obj    → calls __add__

# A JIT can specialize:
# "I've seen int + int 1000 times → compile to: ADD_I64 instruction"
# "Guard: if either arg is NOT int → fall back to interpreter"

class SpecializedAdd:
    """Example of type-specialized addition."""

    def __init__(self):
        self.specializations = {}

    def __call__(self, a, b):
        key = (type(a), type(b))
        if key not in self.specializations:
            self.specializations[key] = self._compile(key)
        return self.specializations[key](a, b)

    def _compile(self, types):
        ta, tb = types
        if ta == int and tb == int:
            # "Compiled" fast path for int+int
            return lambda a, b: a + b   # in reality: native machine code
        elif ta == float and tb == float:
            return lambda a, b: a + b
        else:
            # Generic fallback
            return lambda a, b: a + b

fast_add = SpecializedAdd()
```

---

## Guard failure and deoptimization

```python
class GuardedCode:
    """Compiled code with type guards — deoptimizes if guards fail."""

    def __init__(self, compiled_func, expected_types, fallback):
        self.compiled = compiled_func
        self.expected_types = expected_types
        self.fallback = fallback
        self.guard_failures = 0

    def __call__(self, *args):
        # Check guards
        for arg, expected in zip(args, self.expected_types):
            if type(arg) != expected:
                self.guard_failures += 1
                if self.guard_failures > 10:
                    # Too many failures — this specialization is wrong
                    # Recompile with broader types or stay in interpreter
                    print("  Deoptimizing: too many guard failures")
                return self.fallback(*args)

        # Guards passed — use fast compiled code
        return self.compiled(*args)
```

---

## Inline caching

```python
class InlineCache:
    """Cache the result of type lookups for attribute access."""

    def __init__(self):
        self.cache = {}   # (type, attr_name) → method

    def get_method(self, obj, attr_name):
        key = (type(obj), attr_name)
        if key in self.cache:
            return self.cache[key]

        # Slow path: actual attribute lookup
        method = getattr(type(obj), attr_name)
        self.cache[key] = method
        return method

# In a real JIT: inline cache is embedded directly in the compiled code
# Monomorphic: one type seen → direct call
# Polymorphic: 2-4 types → if/else chain
# Megamorphic: many types → generic lookup (give up specialization)
```

---

## CPython's JIT (PEP 744, Python 3.13+)

Python 3.13 introduced an experimental copy-and-patch JIT:

- Compiles hot bytecode sequences to machine code
- Uses **copy-and-patch** (pre-compiled templates stitched together)
- Faster than full LLVM JIT compilation
- 5-10% speedup on benchmarks

```bash
# Enable the JIT (experimental)
python -X jit my_script.py

# Check if JIT is available
python -c "import sys; print(sys._jit)"
```

---

## Practice Exercises

1. **Build a toy interpreter** for a simple expression language, then add a tracing JIT layer.
2. **Implement type specialization** for a + operator that handles int, float, and str.
3. **Add guards and deoptimization** — compile optimistic code that falls back on type mismatch.
4. **Implement inline caching** for method dispatch in a simple object system.
5. **Benchmark** interpreted vs JIT-compiled execution for a tight loop.
6. **Study CPython's copy-and-patch JIT** — read the source in `Python/jit.c`.
