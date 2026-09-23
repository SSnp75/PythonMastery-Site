---
title: "Kernel Tracing"
description: Trace syscalls and kernel events with perf, ftrace and eBPF from Python
---

# Kernel Tracing <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>🔧 Embedded & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="../../systems/advanced/profiling/">Profiling</a>, <a href="../../systems/research/ebpf/">eBPF</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Why trace the kernel at all
- [x] The main Linux tracing tools (strace, perf, ftrace, eBPF)
- [x] Trace system calls from and about a program
- [x] Use eBPF/BCC from Python
- [x] Read tracing output to debug performance

!!! note "Linux-only, requires elevated privileges"
    Kernel tracing is a **Linux** capability and needs root/`CAP_SYS_ADMIN`. The tools here (perf, ftrace, eBPF/BCC) don't exist on this Windows host, so the commands and BCC snippets aren't run-verified — they follow the documented interfaces. To use them you need a Linux system with the tracing tools and kernel support installed.

---

## Why trace the kernel

Application profilers (see [Profiling](../systems/advanced/profiling.md)) show where *your Python code* spends time. But when a program is slow because of what it asks the *operating system* to do — reading files, waiting on the network, spawning processes, contending for locks — you need to see below your code, into the **kernel**. Kernel tracing reveals the system calls a program makes, how long they take, and what the kernel does in response.

```
   your Python code          ← profilers see here
   ─────────────────────
   system calls (read,       ← kernel tracing sees here
   write, open, futex...)
   ─────────────────────
   kernel: schedulers, I/O,
   network stack, filesystems
```

---

## The Linux tracing toolbox

| Tool | What it does | Overhead |
|---|---|---|
| **strace** | Log every syscall a process makes | High (good for debugging, not production) |
| **perf** | Sample CPU, count events, profile system-wide | Low–medium |
| **ftrace** | Built-in kernel function tracer (via `/sys/kernel/debug/tracing`) | Low |
| **eBPF** | Run safe custom programs *inside* the kernel to trace anything | Very low (production-grade) |

The trend is toward **eBPF** — it's programmable, low-overhead, and safe enough to run on production systems.

---

## strace: see the syscalls

The quickest way to see what a program asks the kernel to do:

```bash
strace -c python3 myscript.py     # -c summarizes syscall counts and time
```

Example summary (illustrative):

```text
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 42.11    0.001234          12       100           read
 28.05    0.000822           8       100           write
 ...
```

This instantly answers "is my program spending its time in `read`, `futex`, `poll`…?" — often revealing that a "slow" program is actually waiting on I/O or locks, not computing.

---

## perf: profile the whole system

`perf` samples what's running across the system, including kernel time:

```bash
perf record -g python3 myscript.py    # -g captures call graphs
perf report                            # interactive breakdown
```

It attributes CPU time down into kernel functions, so you can see, say, that time is going into the network stack or the filesystem — invisible to a pure-Python profiler.

---

## eBPF from Python (BCC)

**eBPF** lets you load small, verified programs into the kernel that fire on events (a syscall, a function entry, a network packet). The **BCC** toolkit exposes this from Python: you write the in-kernel probe in a C snippet and the orchestration in Python.

```python
from bcc import BPF     # requires bcc installed on Linux

# In-kernel probe: fire on every open() syscall
program = r"""
int trace_open(void *ctx) {
    bpf_trace_printk("open() called\\n");
    return 0;
}
"""

b = BPF(text=program)
b.attach_kprobe(event=b.get_syscall_fnname("openat"), fn_name="trace_open")

print("tracing openat()... Ctrl-C to stop")
b.trace_print()      # stream events as they fire
```

This attaches a **kprobe** (kernel probe) to the `openat` syscall; every time *any* process opens a file, the probe fires and prints. Real eBPF tools (like the `bcc` and `bpftrace` suites — `execsnoop`, `opensnoop`, `biolatency`) do exactly this to trace process launches, file opens, disk latency, and more with negligible overhead.

!!! tip "Reach for prebuilt eBPF tools first"
    Before writing your own probe, check the `bcc-tools`/`bpftrace` collection — `opensnoop`, `execsnoop`, `tcpconnect`, `biolatency`, and dozens more already cover common questions. Write custom eBPF only when nothing off-the-shelf answers your question. See the [eBPF](../systems/research/ebpf.md) topic for depth.

---

## Reading the output to debug

The workflow for a "mysteriously slow" program:

1. **`strace -c`** — is it syscall-bound? Which syscall dominates?
2. If it's waiting (lots of time in `read`, `poll`, `futex`) → it's I/O or lock contention, not CPU.
3. **`perf`** — where does CPU time go, including kernel?
4. **eBPF tool** — drill into the specific subsystem (disk latency with `biolatency`, slow opens with `opensnoop`).

This top-down path moves you from "the program is slow" to a specific kernel-level cause — the kind of insight application profilers can't give.

---

## Practice exercises

1. On a Linux machine, run `strace -c` on a simple Python script that reads a file in a loop, and identify the dominant syscall.
2. Use `strace -e trace=network` on a script that makes an HTTP request and observe the connect/send/recv calls.
3. Run the `opensnoop` bcc tool (if available) and watch which files programs open system-wide.
4. Explain the difference between what `cProfile` shows and what `strace` shows for the same program.
5. Describe a performance problem that a kernel tracer would reveal but a Python profiler would completely miss.
