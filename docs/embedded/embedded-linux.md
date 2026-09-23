---
title: "Python for Embedded Linux"
description: Run Python on Raspberry Pi and embedded Linux — GPIO, daemons and cross-compiling
---

# Python for Embedded Linux <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🔧 Embedded & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="../../automation/scripting/">Automation & Scripting</a>, <a href="embedded-python/">Embedded Python</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Where embedded Linux sits between a PC and a microcontroller
- [x] Control GPIO from full CPython
- [x] Run Python as a background service (daemon)
- [x] Cross-compile and deploy to a target board
- [x] Manage resource constraints on small Linux devices

!!! note "This topic targets embedded Linux boards"
    Examples assume a device like a Raspberry Pi running Linux, with hardware pins and a systemd init. They use documented library and OS APIs and aren't run-verified on this desktop. To follow along you need a board (Pi, BeagleBone, or similar).

---

## Embedded Linux vs microcontrollers

Unlike a microcontroller running [MicroPython](embedded-python.md), an embedded Linux board (Raspberry Pi, BeagleBone, industrial gateways) runs a **full Linux OS and full CPython**. You get the entire standard library, pip, and PyPI — but on modest hardware and often headless (no screen).

```
   Microcontroller        Embedded Linux         Desktop/Server
   MicroPython            full CPython           full CPython
   ~256 KB RAM            256 MB–2 GB RAM        GBs
   no OS / RTOS           real Linux              Linux/Windows
   bare-metal pins        GPIO via OS drivers     no GPIO
```

So "Python for embedded Linux" is mostly normal Python — with three twists: hardware pins, running as an unattended service, and tight-ish resources.

---

## Controlling GPIO

On a Raspberry Pi, the modern library is **`gpiozero`** (friendly, high-level, built on lower-level drivers):

```python
from gpiozero import LED, Button    # pip install gpiozero
from time import sleep

led = LED(17)        # BCM pin 17
button = Button(2)

button.when_pressed = led.on        # event-driven
button.when_released = led.off

while True:
    sleep(1)
```

Or a simple blink:

```python
from gpiozero import LED
from time import sleep

led = LED(17)
while True:
    led.on();  sleep(0.5)
    led.off(); sleep(0.5)
```

Because it's full CPython, you can freely combine hardware control with the whole ecosystem — read a sensor and POST it to an API with `requests`, log to a database, or serve a web dashboard, all in one program.

---

## Running as a service (daemon)

Embedded devices run **headless and unattended** — your program must start on boot, restart if it crashes, and log somewhere persistent. On Linux, **systemd** manages this. You write a unit file:

```ini
# /etc/systemd/system/sensor.service
[Unit]
Description=Sensor logging service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/sensor.py
Restart=always              # restart if it crashes
User=pi

[Install]
WantedBy=multi-user.target
```

Then enable and start it:

```bash
sudo systemctl enable sensor.service   # start on boot
sudo systemctl start sensor.service    # start now
sudo systemctl status sensor.service   # check it
journalctl -u sensor.service -f        # follow its logs
```

`Restart=always` gives you crash recovery for free, and `journalctl` centralizes logs. Your Python code should use the `logging` module (see [Automation & Scripting](../automation/scripting.md)) so its output lands in the journal.

!!! tip "Design for unattended operation"
    A daemon has no one watching. Handle errors so a transient failure (a sensor hiccup, a dropped network) is logged and retried, not fatal. Catch `SIGTERM` for graceful shutdown so systemd can stop it cleanly.

---

## Cross-compiling and deployment

Embedded boards are slow to build on. **Cross-compiling** means building on your fast PC for the target's architecture (often ARM), then deploying the artifact.

For pure-Python code there's nothing to compile — you just copy files. The complication is **C-extension dependencies** (numpy, cryptography, pillow): their compiled wheels must match the target's architecture.

- **`pip` wheels** — many packages publish prebuilt ARM wheels (`manylinux`/`aarch64`), so `pip install` on the Pi just works.
- **Docker with QEMU / buildx** — build an ARM image on your PC (`docker buildx build --platform linux/arm64`) and run it on the board. Reproducible and increasingly the standard.
- **Yocto / Buildroot** — build a whole custom Linux image with your Python app baked in. Heavy tooling, used for production embedded products at scale.

For deployment, common approaches are `rsync`/`scp` of the code, a git pull on the device, or shipping a Docker image.

---

## Resource constraints

Embedded Linux is roomier than a microcontroller but far tighter than a server:

- **Limited RAM** (256 MB–1 GB typical). Avoid loading huge datasets; stream instead. Watch memory-hungry libraries.
- **Slow/limited storage** — often an SD card with limited write cycles. Minimize logging to disk (log to journald with rotation), avoid constant writes that wear the card.
- **Modest CPU** — heavy numeric work is slow; offload to C extensions or accept lower rates.
- **Power** — battery/solar devices need you to sleep the CPU and minimize wakeups.
- **Startup time** — a large Python app with many imports can be slow to boot; keep dependencies lean.

---

## Practice exercises

1. Write a `gpiozero` program that lights an LED when a sensor reading crosses a threshold, and turns it off otherwise.
2. Write a systemd unit for a Python script, enable it, and confirm it restarts after you `kill` the process.
3. Add `logging` to a daemon so its output appears in `journalctl`, including a startup and shutdown message.
4. Add a `SIGTERM` handler that stops your loop cleanly, and verify `systemctl stop` shuts it down gracefully.
5. Explain when you'd choose a Docker/buildx deployment over `rsync`-ing files to the board.
