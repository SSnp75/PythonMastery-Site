---
title: "Systems Projects"
description: Low-level and DevOps tooling — monitors, tracers, CLI tools and integrations
---

# Systems Projects <span class="pm-badge pm-badge-advanced">Level 5-6</span>

<div class="pm-topic-header">
  <strong>🛠️ Projects</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Days to weeks each</span>
    <span>📚 Prereqs: <a href="../embedded/system-monitoring.md">System Monitoring</a>, <a href="../systems/advanced/profiling.md">Profiling</a></span>
  </div>
</div>

---

These projects work close to the operating system and infrastructure — the kind of tooling that keeps systems running and observable. They exercise the Embedded & Systems and Performance material.

---

## 1. System monitor + alerter

**Goal:** collect CPU/memory/disk metrics, alert when thresholds are crossed.

- **Skills:** `psutil`, threshold logic, notifications, running as a service.
- **Minimal version:** print metrics on a loop, alert when CPU > 90%.
- **Stretch:** export to Prometheus, a dashboard, consecutive-breach logic, run as a systemd service. Directly builds the [System Monitoring](../embedded/system-monitoring.md) example out into a real tool.

## 2. Log analyzer / aggregator

**Goal:** parse log files, extract structured data, and report patterns (error rates, top offenders).

- **Skills:** file I/O, regex, `collections`, maybe a small web view.
- **Minimal version:** count log levels (ERROR/WARN/INFO) in a file.
- **Stretch:** tail live logs, time-window analysis, alert on error spikes, handle multiple formats. Great use of [Automation & Scripting](../automation/scripting.md).

## 3. A profiler / benchmark harness

**Goal:** a tool that times and compares implementations, reporting stats.

- **Skills:** `time.perf_counter`, statistics, decorators, reporting.
- **Minimal version:** a decorator that times a function and prints the result.
- **Stretch:** multiple runs with percentiles, comparison tables, memory tracking, plots. Applies the [Profiling](../systems/advanced/profiling.md) topic.

## 4. A CLI dev-ops tool

**Goal:** a polished command-line tool that automates a real workflow (deploys, backups, environment setup).

- **Skills:** `argparse`/Click/Typer, `subprocess`, config files, good UX and error messages.
- **Minimal version:** one subcommand that does something useful with clear `--help`.
- **Stretch:** multiple subcommands, config-driven, dry-run mode, packaged for `pip install`. See [CLI Tools](../web/competent/cli-tools.md) and [Packaging](../web/competent/packaging.md).

## 5. Config-drift detector

**Goal:** compare a system's actual config against a desired spec and report differences.

- **Skills:** parsing config, set/diff logic, idempotency thinking.
- **Minimal version:** diff two config files and print add/remove.
- **Stretch:** apply changes, multiple hosts, git-backed desired state. This generalizes the tested diff from [Networking Automation](../embedded/networking-automation.md).

## 6. A tiny service supervisor

**Goal:** start, monitor, and restart child processes if they die (a mini process manager).

- **Skills:** `subprocess`, signals, health checks, graceful shutdown.
- **Minimal version:** launch a process and restart it if it exits.
- **Stretch:** multiple processes, config file, restart backoff, log capture. Teaches the mechanics behind systemd/supervisord.

---

## Why systems projects are valuable

They force you to deal with the messy real world: processes, signals, files, the OS, failure. This "ops-aware" skill set — building tools that run unattended, observe systems, and recover from failure — is exactly what distinguishes a developer who can *operate* software from one who can only write it.

!!! tip "Make it run unattended"
    A systems tool's real test is running for days without you watching. Add logging ([Automation & Scripting](../automation/scripting.md)), handle `SIGTERM` for clean shutdown, and make it recover from transient errors. That robustness is the whole point.

For the frontier, see [Research Projects](research.md).
