---
title: "Real-time Systems"
description: Real-time constraints, scheduling and why Python needs care in timing-critical code
---

# Real-time Systems <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>🔧 Embedded & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="../../systems/proficient/threading/">Threading</a>, <a href="../../core/advanced/garbage-collection/">Garbage Collection</a></span>
  </div>
</div>

---

## What you'll learn

- [x] The difference between soft and hard real-time
- [x] What jitter is and how to measure it
- [x] Why Python is a poor fit for hard real-time
- [x] Mitigation strategies when you must use Python
- [x] When to reach for C, an RTOS, or an FPGA instead

---

## What "real-time" actually means

Real-time does **not** mean "fast." It means **predictable** — the system must respond within a guaranteed time bound, every time. A slow-but-punctual system can be real-time; a fast-but-erratic one is not.

```
  Hard real-time:  missing a deadline = system failure
                   (airbag, pacemaker, motor control, flight surfaces)

  Soft real-time:  missing a deadline = degraded quality, not disaster
                   (video playback, audio, game frames, live dashboards)
```

- **Hard real-time** — a missed deadline is a catastrophic failure. Deploying an airbag 50 ms late is useless. These systems need guaranteed worst-case timing.
- **Soft real-time** — deadlines matter for quality but occasional misses are tolerable. A dropped video frame is annoying, not dangerous.

The defining metric is the **worst case**, not the average. "Usually 1 ms" is meaningless for hard real-time; "never more than 2 ms" is what counts.

---

## Jitter: the enemy of predictability

**Jitter** is the variation in timing — how much actual intervals deviate from the target. A task meant to run every 10 ms that sometimes runs at 9.7 ms and sometimes at 10.6 ms has jitter. Measuring it tells you how predictable your timing really is. Runnable:

```python
import time, statistics

def measure_jitter(target_period: float, samples: int) -> dict[str, float]:
    deltas = []
    prev = time.perf_counter()
    for _ in range(samples):
        time.sleep(target_period)
        now = time.perf_counter()
        deltas.append(now - prev)          # actual interval
        prev = now
    errors = [abs(d - target_period) for d in deltas]
    return {"mean_error_ms": statistics.mean(errors) * 1000,
            "max_error_ms": max(errors) * 1000}
```

```python
result = measure_jitter(target_period=0.01, samples=20)   # aim for 10 ms
print(f"mean error: {result['mean_error_ms']:.3f} ms")
print(f"max error:  {result['max_error_ms']:.3f} ms")
```

Illustrative output (values vary by machine and OS load):

```text
mean error: 0.374 ms
max error:  0.607 ms
```

Asking for a 10 ms sleep, we got errors of a few hundred microseconds up to over half a millisecond — on an idle desktop. `time.perf_counter()` is the right clock for this (high-resolution, monotonic). The key lesson: `time.sleep()` guarantees a *minimum* delay, never a maximum. That non-guarantee is exactly what makes general-purpose Python unsuitable for hard deadlines.

!!! note "Your numbers will differ"
    Jitter depends on your OS scheduler, CPU load, and power state, so exact figures change every run. Under load, the max error can spike to *milliseconds* — which is why worst-case, not average, is what matters.

---

## Why Python struggles with hard real-time

Several parts of Python's design work against guaranteed timing:

- **Garbage collection pauses.** Python's cyclic garbage collector can run at unpredictable moments, introducing pauses right when you need determinism. (You can disable it with `gc.disable()`, at the cost of managing memory carefully.)
- **The GIL.** Only one thread runs Python bytecode at a time, so a "real-time" thread can be blocked by another thread holding the GIL. See [Threading](../systems/proficient/threading.md).
- **Dynamic everything.** Attribute lookups, allocations, and dispatch happen at runtime with variable cost — no guaranteed instruction timing.
- **OS scheduling.** On a general-purpose OS (Windows, stock Linux), your process competes with everything else and can be preempted at any time.

The result: Python can do **soft** real-time comfortably (audio, dashboards, robotics at moderate rates), but **hard** real-time — microsecond-guaranteed motor control, safety systems — is the wrong job for it.

---

## Mitigation strategies

When you must use Python in timing-sensitive code, you can push soft real-time further:

- **Control GC.** `gc.disable()` during critical sections, or `gc.freeze()` to skip already-created objects, then collect manually at safe points.
- **Pre-allocate.** Allocate buffers and objects up front so no allocation (and no GC pressure) happens in the hot loop.
- **Use a real-time OS or `PREEMPT_RT` Linux.** A real-time kernel gives far tighter scheduling guarantees than stock Linux/Windows.
- **Raise process priority / pin to a CPU.** Real-time scheduling classes (`SCHED_FIFO` on Linux) and CPU affinity reduce preemption.
- **Push the hard part into C.** Do the timing-critical work in a C extension or a microcontroller, and use Python for orchestration, config, and the soft parts.
- **Busy-wait for very short, precise delays** (spinning on `perf_counter`) instead of `time.sleep`, accepting the CPU cost — only for tiny intervals.

!!! tip "Right tool for the tier"
    Match the technology to the requirement: Python for soft real-time and orchestration; C/C++ or Rust for tight loops; a microcontroller or **RTOS** (FreeRTOS, Zephyr) for hard deadlines; an **FPGA** for nanosecond-deterministic signal work. A common, healthy architecture is Python on top coordinating a C/microcontroller layer underneath.

---

## A soft real-time control loop

A moderate-rate control loop (e.g. 50 Hz robotics) is well within Python's comfort zone if you compensate for drift:

```python
import time

def control_loop(rate_hz: float, iterations: int) -> None:
    period = 1.0 / rate_hz
    next_tick = time.perf_counter()
    for _ in range(iterations):
        # ... read sensors, compute, actuate ...
        next_tick += period
        sleep_for = next_tick - time.perf_counter()
        if sleep_for > 0:
            time.sleep(sleep_for)          # sleep only the remaining time
        # if sleep_for < 0 we're behind — the loop self-corrects next tick
```

Sleeping until an absolute `next_tick` (rather than sleeping a fixed `period` each time) prevents accumulated drift: if one iteration runs long, the next sleeps less to catch up. This is the standard pattern for keeping a soft real-time loop on schedule.

---

## Practice exercises

1. Run `measure_jitter` while the machine is idle, then again while running a CPU-heavy task in parallel, and compare the max error.
2. Add a percentile to the jitter report (e.g. 99th percentile error) — often more meaningful than the mean for real-time.
3. Implement the `control_loop` with a counter of how many iterations ran late (missed their deadline).
4. Experiment with `gc.disable()` around a tight loop and measure whether max jitter improves.
5. Write a short note: for a 1 kHz motor controller, why would you not implement the control law in CPython, and what would you use instead?
