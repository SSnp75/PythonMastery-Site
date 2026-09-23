---
title: "System Monitoring"
description: Collect metrics, export them and alert when a system misbehaves
---

# System Monitoring <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🔧 Embedded & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisites: <a href="../../automation/scripting/">Automation & Scripting</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Collect CPU, memory and disk metrics
- [x] Turn raw readings into alerts with thresholds
- [x] Export metrics for Prometheus/Grafana
- [x] Build a simple monitoring loop
- [x] Understand agents vs pull-based scraping

---

## The monitoring pipeline

Every monitoring system, from a 20-line script to Datadog, follows the same four stages:

```
  COLLECT  →  PROCESS  →  EXPORT/STORE  →  ALERT
  (read      (thresholds,  (Prometheus,     (notify when
   metrics)   rates)        time-series DB)   something's wrong)
```

We'll build the pieces in Python, keeping the logic runnable with pure stdlib and showing where real libraries plug in.

---

## Collecting metrics

The de-facto library is **`psutil`** — cross-platform access to CPU, memory, disk, network, and processes.

```python
import psutil   # pip install psutil

cpu = psutil.cpu_percent(interval=1)       # % over a 1-second sample
mem = psutil.virtual_memory().percent      # % RAM used
disk = psutil.disk_usage("/").percent      # % of root filesystem used

print(f"CPU {cpu}%  MEM {mem}%  DISK {disk}%")
# e.g. -> CPU 12.5%  MEM 55.0%  DISK 88.0%
```

!!! note "`psutil` snippet needs the package installed"
    The collection code above uses `psutil`, which isn't part of the standard library, so it isn't run-verified here. The **processing and alerting logic below is pure stdlib and fully tested.** On a system without `psutil`, you can read some metrics from `/proc` (Linux) or `os`/`shutil` (e.g. `shutil.disk_usage`).

---

## Processing: turning readings into alerts

The valuable part isn't reading a number — it's deciding when a number is a *problem*. A threshold check is the simplest useful processing step. Fully runnable:

```python
def check_thresholds(metrics: dict[str, float],
                     limits: dict[str, float]) -> list[str]:
    """Return an alert string for each metric that exceeds its limit."""
    alerts = []
    for name, value in metrics.items():
        limit = limits.get(name)
        if limit is not None and value > limit:
            alerts.append(f"ALERT {name}={value} exceeds {limit}")
    return alerts
```

```python
sample = {"cpu_percent": 92.0, "mem_percent": 55.0, "disk_percent": 88.0}
limits = {"cpu_percent": 90.0, "mem_percent": 90.0, "disk_percent": 85.0}

for line in check_thresholds(sample, limits):
    print(line)
```

Output:

```text
ALERT cpu_percent=92.0 exceeds 90.0
ALERT disk_percent=88.0 exceeds 85.0
```

CPU and disk breached their limits; memory (55% vs 90%) stayed quiet. Real systems add nuance — alert only if a threshold is exceeded for *N consecutive samples* to avoid firing on momentary spikes — but this is the core idea.

---

## A simple monitoring loop

Combine collection, processing, and action into a loop:

```python
import time

def monitor(limits: dict[str, float], interval: int = 5) -> None:
    while True:
        metrics = collect_metrics()             # your psutil-based collector
        for alert in check_thresholds(metrics, limits):
            notify(alert)                        # email, Slack, PagerDuty...
        time.sleep(interval)
```

For anything long-lived, run this as a proper background service (systemd on Linux, a Windows service) and log to a file — see [Automation & Scripting](../automation/scripting.md) for scheduling and logging patterns.

---

## Exporting for Prometheus + Grafana

The industry-standard stack is **Prometheus** (scrapes and stores metrics) + **Grafana** (dashboards). Your app exposes metrics on an HTTP endpoint; Prometheus *pulls* them on a schedule.

```python
from prometheus_client import Gauge, start_http_server   # pip install prometheus-client
import psutil, time

cpu_gauge = Gauge("system_cpu_percent", "CPU usage percent")
mem_gauge = Gauge("system_mem_percent", "Memory usage percent")

start_http_server(8000)     # metrics now at http://localhost:8000/metrics

while True:
    cpu_gauge.set(psutil.cpu_percent())
    mem_gauge.set(psutil.virtual_memory().percent)
    time.sleep(5)
```

!!! note "Requires prometheus-client + a Prometheus server"
    This follows the documented `prometheus_client` API. Prometheus then scrapes `/metrics`, and Grafana graphs it. The pattern: your process *publishes* current values; the monitoring system *pulls* them.

---

## Push vs pull, agents vs libraries

Two architectural choices you'll encounter:

| | **Pull (scrape)** | **Push** |
|---|---|---|
| Who initiates | Monitoring server scrapes your endpoint | Your app pushes to a collector |
| Example | Prometheus | StatsD, Graphite, push gateways |
| Good for | Long-running services | Short-lived jobs, batch tasks |

- **Agent** — a separate process (Prometheus Node Exporter, Telegraf, the Datadog agent) runs on the host and collects system metrics for you. Great for standard host metrics you don't want to code yourself.
- **Library** — you instrument your own app (like `prometheus_client` above) to expose *application* metrics (requests/sec, queue depth) the agent can't know about.

Most real setups use both: an agent for host metrics, a library for app-specific ones.

---

## Practice exercises

1. Extend `check_thresholds` to only alert if a metric exceeds its limit for 3 consecutive samples (add state).
2. Write a collector using `shutil.disk_usage` and `/proc/loadavg` (Linux) or `os` calls — no `psutil` — and feed it into `check_thresholds`.
3. Add severity levels (warning vs critical) with two thresholds per metric.
4. Expose one real metric via `prometheus_client` and view it at `/metrics` (install the package locally).
5. Explain when you'd use a push model instead of Prometheus's pull model, with a concrete example.
