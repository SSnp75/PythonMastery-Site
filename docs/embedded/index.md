---
title: "Embedded & Systems"
description: Python at the hardware and OS boundary — microcontrollers, devices, real-time and kernel-level work
---

# 🔧 Embedded & Systems

**Python where it meets the metal — from microcontrollers and sensors to real-time control, device fleets and the Linux kernel.**

This section covers the low-level end of Python: driving hardware, testing firmware, operating devices unattended, and observing what the system does beneath your code. Some topics run on ordinary Python; others target real boards, Linux kernels, or robotics rigs, and are noted as such.

## Topics

<ul class="pm-subtopics" markdown="1">
- [📊 System Monitoring](system-monitoring.md) — collect metrics, alert on thresholds, export to Prometheus
- [🔌 Firmware Testing](firmware-testing.md) — serial protocols, framing, test harnesses, device simulation
- [🎛️ Hardware Simulation](hardware-simulation.md) — discrete-event simulation and testbeds
- [⏱️ Real-time Systems](real-time-systems.md) — soft vs hard real-time, jitter, why Python needs care
- [🌐 Networking Automation](networking-automation.md) — SSH device config, idempotency, NetOps
- [🐍 Embedded Python](embedded-python.md) — MicroPython & CircuitPython on microcontrollers
- [🖥️ Python for Embedded Linux](embedded-linux.md) — Raspberry Pi, GPIO, daemons, cross-compiling
- [🤖 Robotics Middleware](robotics-middleware.md) — ROS 2 nodes, topics and pub/sub
- [🔬 Kernel Tracing](kernel-tracing.md) — strace, perf, ftrace and eBPF from Python
</ul>

---

## How the topics relate

```
   Microcontroller  →  Embedded Linux  →  Full systems
   (Embedded Python)   (Embedded Linux)   (System Monitoring,
                                           Networking Automation)

   Testing & modeling:  Firmware Testing, Hardware Simulation
   Timing & internals:  Real-time Systems, Kernel Tracing
   Robotics:            Robotics Middleware (ties sensors→control→actuators)
```

**A suggested path:** start with **Embedded Python** (Python on a chip) and **Embedded Linux** (Python on a small computer) to ground the hardware model. Add **Firmware Testing** and **Hardware Simulation** for testing without (or before) hardware. Then **System Monitoring** and **Networking Automation** for operating real systems and fleets. Finally, **Real-time Systems**, **Kernel Tracing**, and **Robotics Middleware** for the demanding, timing- and internals-heavy end.

!!! tip "Match Python to the tier"
    A recurring theme across this section: Python excels at orchestration, testing, and soft real-time — and hands off the hardest timing-critical work to C, a microcontroller, an RTOS, or the kernel. The best embedded architectures use Python on top of a lower, faster layer.
