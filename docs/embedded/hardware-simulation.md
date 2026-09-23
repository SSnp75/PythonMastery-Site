---
title: "Hardware Simulation"
description: Model and simulate hardware behavior with discrete-event simulation
---

# Hardware Simulation <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🔧 Embedded & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="../../core/intermediate/iterators-generators/">Iterators & Generators</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Why simulate hardware at all
- [x] Build a discrete-event simulation engine
- [x] Model periodic sensors and one-off events
- [x] Use `simpy` for realistic simulations
- [x] Build a testbed around a simulated device

---

## Why simulate hardware

Real hardware is scarce, slow, and sometimes doesn't exist yet. Simulation lets you develop and test the software *before* the board arrives, run thousands of scenarios in seconds, and reproduce rare timing bugs on demand. It's how you test firmware logic, protocol handling, and control loops without a physical rig.

The dominant technique is **discrete-event simulation (DES)**: instead of advancing time in tiny fixed steps, you jump directly from one *event* to the next. A simulated clock holds the "current time," and events are processed in time order. This is enormously more efficient than stepping through idle time.

```
  Real time:      ────────────────────────────▶  (continuous, mostly idle)
  DES:            •────────•──•──────────•──▶     (jump event → event)
                  t=1      t=2 t=2.5     t=3
```

---

## A discrete-event engine from scratch

The core is a **priority queue of events keyed by time**. We pop the earliest, advance the clock to it, process it, and repeat. Fully runnable:

```python
import heapq

class Simulation:
    def __init__(self) -> None:
        self.now = 0.0
        self._queue: list[tuple[float, int, str]] = []
        self._seq = 0                       # tiebreaker for equal times
        self.log: list[tuple[float, str]] = []

    def schedule(self, delay: float, event: str) -> None:
        """Schedule an event `delay` time-units from now."""
        heapq.heappush(self._queue, (self.now + delay, self._seq, event))
        self._seq += 1

    def run(self, until: float) -> None:
        while self._queue and self._queue[0][0] <= until:
            t, _, event = heapq.heappop(self._queue)
            self.now = t                    # advance the clock to the event
            self.log.append((t, event))
            if event == "sensor_read":      # periodic: reschedule itself
                self.schedule(1.0, "sensor_read")
```

**Why the `_seq` tiebreaker:** if two events land at the same time, the heap needs a way to order them without comparing the event strings. The incrementing sequence number guarantees a stable, deterministic order.

Running a scenario — a sensor reading every second plus a one-off button press:

```python
sim = Simulation()
sim.schedule(1.0, "sensor_read")     # first read at t=1, then self-repeats
sim.schedule(2.5, "button_press")
sim.run(until=3.0)

print("event log:", sim.log)
```

Output:

```text
event log: [(1.0, 'sensor_read'), (2.0, 'sensor_read'), (2.5, 'button_press'), (3.0, 'sensor_read')]
```

The sensor fires at 1.0, 2.0, 3.0 (rescheduling itself each time), and the button press slots in at 2.5 — all in correct time order, with the clock jumping straight between events. No real time elapsed; the whole 3-second scenario ran instantly.

---

## Using `simpy` for real simulations

Hand-rolling a scheduler is great for understanding DES, but for anything substantial use **`simpy`**, which builds simulations on Python generators — you `yield` timeouts and the framework advances the clock.

```python
import simpy   # pip install simpy

def sensor(env, period):
    while True:
        print(f"t={env.now}: sensor read")
        yield env.timeout(period)      # advance simulated time by `period`

env = simpy.Environment()
env.process(sensor(env, period=1.0))
env.run(until=3)
# t=0: sensor read
# t=1: sensor read
# t=2: sensor read
```

!!! note "`simpy` snippet needs the package"
    This follows simpy's documented API and isn't run-verified here (the from-scratch engine above **is** tested). simpy adds resources (limited pumps, servers), queues, and process interaction — everything you'd hand-code eventually — so reach for it once your model outgrows a toy.

---

## Building a testbed

Simulation shines as a **testbed**: wrap a simulated device so your real software can talk to it exactly as it would to hardware.

```python
class SimulatedThermostat:
    """Models a heater warming a room toward a setpoint."""
    def __init__(self, temp=18.0, setpoint=21.0):
        self.temp = temp
        self.setpoint = setpoint
        self.heating = False

    def tick(self) -> None:
        self.heating = self.temp < self.setpoint
        if self.heating:
            self.temp += 0.5              # heater raises temp
        else:
            self.temp -= 0.1              # ambient cooling

def test_thermostat_reaches_setpoint():
    t = SimulatedThermostat(temp=18.0, setpoint=21.0)
    for _ in range(20):
        t.tick()
    assert t.temp >= 21.0                 # it warmed up to target
```

Now the control software can be tested against this model — thousands of scenarios (different starting temps, setpoints, failures) in a test suite, no physical thermostat required.

---

## When simulation is (and isn't) enough

**Great for:** logic, protocols, control loops, timing *models*, rare-scenario reproduction, pre-hardware development.

**Not a substitute for:** real electrical behavior, true analog timing, actual firmware on real silicon, EMI/noise, manufacturing variance. Simulation validates your *model* of the hardware; only real hardware validates the hardware. Use simulation to catch most bugs cheaply, then confirm on the bench (see [Firmware Testing](firmware-testing.md)).

---

## Practice exercises

1. Add a `"low_battery"` event to the `Simulation` that fires once at t=2.2 and stops the sensor rescheduling.
2. Modify `run` to accept a callback per event type instead of the hard-coded `if event == "sensor_read"`.
3. Model two sensors with different periods (1.0 and 1.5) and verify their interleaved event order.
4. Rebuild the sensor example in `simpy` and compare the code to the from-scratch version.
5. Extend `SimulatedThermostat` with a broken-heater failure mode and write a test asserting the temperature never reaches setpoint.
