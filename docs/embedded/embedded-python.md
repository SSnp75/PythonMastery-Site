---
title: "Embedded Python"
description: Run Python on microcontrollers with MicroPython and CircuitPython
---

# Embedded Python <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🔧 Embedded & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="../../core/beginner/python-basics/">Python Basics</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What MicroPython and CircuitPython are
- [x] Read sensors and control pins (GPIO)
- [x] Work within tight memory constraints
- [x] Choose between the two runtimes
- [x] Understand what standard Python features you lose

!!! note "This topic targets real microcontroller hardware"
    The code here runs on a microcontroller (Raspberry Pi Pico, ESP32, etc.), not on a desktop CPython, so the snippets can't be run-verified in this environment. They follow the documented MicroPython/CircuitPython APIs. To try them you need a supported board and its firmware flashed.

---

## Python on a microcontroller

Microcontrollers — the tiny chips inside sensors, appliances, and IoT devices — traditionally run C. **MicroPython** and **CircuitPython** put a real Python interpreter on these chips, so you write firmware in Python instead. You lose some speed and RAM, but gain enormous development speed: edit a file, save, and it runs — no compile-and-flash cycle.

```
   Desktop Python (CPython)        Embedded Python
   ┌────────────────────┐         ┌──────────────────┐
   │ GHz CPU, GBs of RAM │         │ ~100 MHz, ~256 KB │
   │ full stdlib          │   vs   │ tiny subset       │
   │ pip / PyPI           │         │ upip / bundles    │
   └────────────────────┘         └──────────────────┘
```

These are real Python (indentation, functions, classes, exceptions) — just a slimmed-down implementation tuned for kilobytes of RAM.

---

## Blinking an LED (the "hello world" of hardware)

Controlling a GPIO pin — MicroPython style:

```python
from machine import Pin
import time

led = Pin(25, Pin.OUT)      # onboard LED on a Pico is GPIO 25

while True:
    led.value(1)            # on
    time.sleep(0.5)
    led.value(0)            # off
    time.sleep(0.5)
```

The same idea in **CircuitPython** (slightly different API):

```python
import board
import digitalio
import time

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

while True:
    led.value = True
    time.sleep(0.5)
    led.value = False
    time.sleep(0.5)
```

**GPIO** (General-Purpose Input/Output) pins are how the chip talks to the physical world — set a pin high/low to drive an LED or motor, or read a pin to sense a button or sensor.

---

## Reading a sensor

Reading an analog value (e.g. a temperature sensor or potentiometer) via the ADC (analog-to-digital converter):

```python
from machine import ADC, Pin
import time

sensor = ADC(Pin(26))                 # ADC on GPIO 26

while True:
    raw = sensor.read_u16()            # 0..65535
    voltage = raw / 65535 * 3.3        # convert to volts
    print(f"raw={raw}  voltage={voltage:.2f}V")
    time.sleep(1)
```

Digital input with a button:

```python
from machine import Pin

button = Pin(15, Pin.IN, Pin.PULL_UP)  # internal pull-up resistor

if button.value() == 0:                # pressed pulls the pin low
    print("button pressed")
```

Common protocols (**I2C**, **SPI**, **UART**) connect richer peripherals — displays, accelerometers, other chips — and both runtimes provide `machine.I2C`, `machine.SPI`, etc.

---

## Living within constraints

The defining challenge of embedded Python is **scarcity** — often 256 KB of RAM or less. This changes how you code:

- **Memory is precious.** A careless list comprehension can exhaust RAM. Prefer generators, reuse buffers, and avoid holding large structures.
- **Watch garbage collection.** `import gc; gc.collect()` at safe points reclaims memory; unpredictable GC pauses matter more here (see [Real-time Systems](real-time-systems.md)).
- **The stdlib is tiny.** No `os.path` full API, no `requests`, limited `json`. You get a curated subset plus hardware modules (`machine`, `board`).
- **No pip/PyPI.** Libraries come as pre-bundled modules or via `mip`/`upip`, not the full package ecosystem.
- **Floats may be limited.** Some builds use single-precision floats or omit them; integer math is cheaper.

---

## MicroPython vs CircuitPython

They share a common ancestor (CircuitPython is a fork of MicroPython) but differ in philosophy:

| | **MicroPython** | **CircuitPython** |
|---|---|---|
| Origin | The original project | Adafruit's fork, education-focused |
| Editing | REPL + file upload | Board appears as a **USB drive** — edit `code.py`, it runs on save |
| Concurrency | Has `_thread`, `asyncio` | Simpler, no threading |
| Hardware breadth | Very wide (ESP32, Pico, STM32, ...) | Adafruit boards + many others |
| Best for | Performance, broad boards, advanced use | Beginners, rapid prototyping, great docs |

**Rule of thumb:** CircuitPython for the smoothest beginner experience (drag-and-drop editing, superb tutorials); MicroPython when you need more performance, threading, or a board CircuitPython doesn't cover.

---

## When embedded Python fits (and when it doesn't)

**Great for:** prototyping, education, IoT sensors, hobby projects, and products where development speed beats squeezing every cycle.

**Not ideal for:** ultra-low-power designs counting microamps, hard real-time control loops (see [Real-time Systems](real-time-systems.md)), or the smallest/cheapest chips where every byte and cent matters — there, C still rules. A common approach: prototype in MicroPython, then rewrite hot paths (or the whole thing) in C once the design is proven.

---

## Practice exercises

1. Write a MicroPython program that blinks an LED faster each time a button is pressed (read the button, adjust the sleep).
2. Read an analog sensor and turn on an LED only when the value crosses a threshold.
3. Use `gc.mem_free()` to print free memory before and after allocating a large list, and observe the constraint.
4. Compare the LED-blink code in MicroPython vs CircuitPython and list every API difference.
5. Explain a scenario where you'd prototype in MicroPython but ship in C, and what would drive that decision.
