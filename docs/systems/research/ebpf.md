---
title: eBPF
description: Kernel tracing, observability, bcc tools and system-level Python instrumentation
---

# eBPF <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>⚙️ Performance Track · Level 7</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Open-ended</span>
    <span>📚 Prerequisites: Linux, <a href="../../core/advanced/cpython-internals/">CPython Internals</a></span>
  </div>
</div>

---

## What is eBPF?

eBPF (extended Berkeley Packet Filter) runs **sandboxed programs inside the Linux kernel** without modifying kernel source or loading modules. It's used for:

- **Observability** — trace any kernel/userspace function
- **Networking** — packet filtering, load balancing (XDP)
- **Security** — syscall filtering, container policies
- **Profiling** — low-overhead CPU/memory profiling

---

## Python + eBPF with bcc

```python
#!/usr/bin/env python3
"""Trace all open() syscalls system-wide."""
from bcc import BPF

# eBPF program (runs in kernel)
bpf_program = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

BPF_PERF_OUTPUT(events);

struct event_t {
    u32 pid;
    char comm[16];
    char filename[256];
};

int trace_open(struct pt_regs *ctx, const char __user *filename) {
    struct event_t event = {};
    event.pid = bpf_get_current_pid_tgid() >> 32;
    bpf_get_current_comm(&event.comm, sizeof(event.comm));
    bpf_probe_read_user_str(&event.filename, sizeof(event.filename), filename);
    events.perf_submit(ctx, &event, sizeof(event));
    return 0;
}
"""

# Load and attach
b = BPF(text=bpf_program)
b.attach_kprobe(event="do_sys_openat2", fn_name="trace_open")

# Read events from kernel
def print_event(cpu, data, size):
    event = b["events"].event(data)
    print(f"PID={event.pid} COMM={event.comm.decode()} FILE={event.filename.decode()}")

b["events"].open_perf_buffer(print_event)
print("Tracing open() calls... Ctrl-C to exit")
while True:
    b.perf_buffer_poll()
```

---

## bcc tools for Python profiling

```bash
# Trace Python function calls (requires CPython with DTrace support)
sudo /usr/share/bcc/tools/pythoncalls -p $(pgrep python3)

# Trace Python GC events
sudo /usr/share/bcc/tools/pythongc -p $(pgrep python3)

# Profile Python call stacks (flame graph)
sudo /usr/share/bcc/tools/profile -p $(pgrep python3) -f 30 > out.stacks
flamegraph.pl out.stacks > python_flamegraph.svg
```

---

## Tracing CPython internals with USDT

CPython 3.12+ has built-in USDT (User Statically Defined Tracing) probes:

```python
"""Trace Python function entry/exit with eBPF."""
from bcc import BPF, USDT

# Attach to CPython's built-in probes
pid = 12345   # target Python process
u = USDT(pid=pid)
u.enable_probe(probe="function__entry", fn_name="trace_entry")
u.enable_probe(probe="function__return", fn_name="trace_return")

bpf_text = """
#include <uapi/linux/ptrace.h>

int trace_entry(struct pt_regs *ctx) {
    uint64_t addr;
    char funcname[64];
    bpf_usdt_readarg(1, ctx, &addr);
    bpf_probe_read_user_str(&funcname, sizeof(funcname), (void *)addr);
    bpf_trace_printk("ENTER: %s\\n", funcname);
    return 0;
}

int trace_return(struct pt_regs *ctx) {
    bpf_trace_printk("RETURN\\n");
    return 0;
}
"""

b = BPF(text=bpf_text, usdt_contexts=[u])
b.trace_print()
```

---

## Use cases

| Use case | Tool/approach |
|---|---|
| Function call tracing | bcc `funccount`, `trace` |
| Latency histograms | bcc `funclatency` |
| Memory allocation tracking | bcc `memleak` |
| Network packet analysis | XDP programs |
| Security auditing | Seccomp + eBPF |
| Container observability | Cilium, Falco |

---

## Practice Exercises

1. **Write a bcc program** that counts all syscalls made by a Python process.
2. **Trace all file opens** by a specific PID and record to a log file.
3. **Build a latency histogram** for a Python function using USDT probes.
4. **Detect memory leaks** using bcc's memleak tool on a Python process.
5. **Compare overhead** of eBPF tracing vs sys.settrace for function call counting.
