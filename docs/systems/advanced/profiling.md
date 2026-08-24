---
title: Profiling
description: cProfile, line_profiler, py-spy, memory profiling and optimization workflow
---

# Profiling <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance Track · Level 5</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="../proficient/threading/">Threading/Multiprocessing</a></span>
  </div>
</div>

---

## The optimization workflow

```
1. Write correct code first
2. Measure (profile) — find the bottleneck
3. Optimize only the bottleneck
4. Measure again — verify improvement
5. Repeat until fast enough
```

!!! warning "Don't optimize without profiling"
    Programmers' intuition about where code is slow is wrong ~90% of the time. Always profile first.

---

## timeit — micro-benchmarks

```python
import timeit

# Compare two approaches
t1 = timeit.timeit('"-".join(str(n) for n in range(100))', number=10000)
t2 = timeit.timeit('"-".join(map(str, range(100)))', number=10000)
print(f"Generator: {t1:.4f}s")   # ~0.25s
print(f"Map:       {t2:.4f}s")   # ~0.18s (30% faster!)

# From code
def approach_a():
    return sum([x**2 for x in range(1000)])

def approach_b():
    return sum(x**2 for x in range(1000))

print(timeit.timeit(approach_a, number=10000))   # list comp
print(timeit.timeit(approach_b, number=10000))   # generator (slightly slower for sum!)
```

---

## cProfile — function-level profiling

```python
import cProfile
import pstats

def slow_function():
    total = 0
    for i in range(1000):
        total += expensive_calculation(i)
    return total

def expensive_calculation(n):
    return sum(i**2 for i in range(n))

# Profile it
profiler = cProfile.Profile()
profiler.enable()
result = slow_function()
profiler.disable()

# Print results sorted by cumulative time
stats = pstats.Stats(profiler)
stats.sort_stats("cumulative")
stats.print_stats(10)   # top 10 functions
```

Output:
```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     1000    0.005    0.000    2.341    0.002 script.py:8(expensive_calculation)
        1    0.001    0.001    2.342    2.342 script.py:4(slow_function)
     1000    2.336    0.002    2.336    0.002 {built-in method builtins.sum}
```

### From command line:

```bash
python -m cProfile -s cumulative my_script.py
python -m cProfile -o profile.prof my_script.py   # save for analysis
```

### Visualize with snakeviz:

```bash
pip install snakeviz
python -m cProfile -o profile.prof my_script.py
snakeviz profile.prof   # opens interactive visualization in browser
```

---

## line_profiler — line-by-line timing

```python
# pip install line_profiler

# Add @profile decorator (recognized by kernprof)
@profile
def process_data(data):
    # Which line is slow?
    cleaned = [x.strip() for x in data]        # line 1
    filtered = [x for x in cleaned if len(x) > 5]  # line 2
    sorted_data = sorted(filtered)              # line 3
    result = "\n".join(sorted_data)             # line 4
    return result
```

```bash
kernprof -l -v my_script.py
```

Output:
```
Line #  Hits   Time    Per Hit  % Time  Line Contents
=======================================================
     3  1      150.2   150.2    15.1    cleaned = [x.strip() for x in data]
     4  1       82.4    82.4     8.3    filtered = [x for x in cleaned if ...]
     5  1      720.5   720.5    72.4    sorted_data = sorted(filtered)
     6  1       42.1    42.1     4.2    result = "\n".join(sorted_data)
```

Now you know: `sorted()` is the bottleneck (72.4% of time).

---

## py-spy — sampling profiler (no code changes!)

```bash
# Install
pip install py-spy

# Record a flame graph
py-spy record -o flamegraph.svg -- python my_script.py

# Attach to a running process
py-spy record -o flamegraph.svg --pid 12345

# Live top-like view
py-spy top -- python my_script.py
```

Flame graphs show call stacks — wider bars mean more time spent.

---

## Memory profiling

### tracemalloc (built-in)

```python
import tracemalloc

tracemalloc.start()

# Code to profile
data = [list(range(10000)) for _ in range(100)]
processed = [sum(row) for row in data]

snapshot = tracemalloc.take_snapshot()
stats = snapshot.statistics("lineno")

print("Top 5 memory allocations:")
for stat in stats[:5]:
    print(f"  {stat}")

# Compare two snapshots
snapshot1 = tracemalloc.take_snapshot()
# ... do more work ...
snapshot2 = tracemalloc.take_snapshot()
diff = snapshot2.compare_to(snapshot1, "lineno")
for stat in diff[:5]:
    print(f"  {stat}")
```

### memory_profiler

```python
# pip install memory_profiler

@profile   # decorator from memory_profiler
def memory_hungry():
    a = [1] * (10**6)
    b = [2] * (2 * 10**7)
    del b
    return a
```

```bash
python -m memory_profiler my_script.py
```

Output:
```
Line #  Mem usage    Increment  Line Contents
==============================================
     3   45.2 MiB    0.0 MiB   a = [1] * (10**6)
     4  198.0 MiB  152.8 MiB   b = [2] * (2 * 10**7)
     5   45.2 MiB -152.8 MiB   del b
```

---

## Scalene — CPU + memory + GPU profiler

```bash
pip install scalene
scalene my_script.py
```

Scalene gives:
- CPU time (Python vs C code)
- Memory allocation rate
- Memory leaks
- GPU utilization
- Per-line breakdown

---

## Common optimization patterns

```python
# 1. Avoid repeated attribute lookups
# SLOW
for item in large_list:
    item.method()   # attribute lookup each iteration

# FAST
method = large_list[0].method.__func__  # or use local variable
for item in large_list:
    method(item)

# 2. Use local variables in loops
import math
# SLOW
for x in range(1000000):
    y = math.sqrt(x)

# FAST
sqrt = math.sqrt   # local reference
for x in range(1000000):
    y = sqrt(x)

# 3. Use comprehensions over loops
# SLOW
result = []
for x in range(10000):
    result.append(x**2)

# FAST
result = [x**2 for x in range(10000)]

# 4. String concatenation
# SLOW
s = ""
for word in words:
    s += word + " "

# FAST
s = " ".join(words)

# 5. Use set for membership testing
# SLOW — O(n) per lookup
if item in large_list: ...

# FAST — O(1) per lookup
large_set = set(large_list)
if item in large_set: ...
```

---

## Practice Exercises

1. **Profile a real script** with cProfile and identify the top 3 bottlenecks.
2. **Use line_profiler** to find the slowest line in a function and optimize it.
3. **Generate a flame graph** with py-spy for a web application under load.
4. **Use tracemalloc** to find a memory leak in a long-running process.
5. **Optimize a function** from 10s to <1s using profiling-guided techniques.
6. **Compare** the same algorithm implemented with list, generator, numpy — profile all three.
