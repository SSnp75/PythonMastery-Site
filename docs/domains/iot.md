---
title: "Python for IoT"
description: Collect sensor data, message with MQTT, and run on edge devices
---

# Python for IoT <span class="pm-badge pm-badge-proficient">Domain</span>

<div class="pm-topic-header">
  <strong>🌍 Domain Applications</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prereqs: <a href="../embedded/embedded-python.md">Embedded Python</a>, <a href="../automation/scripting.md">Automation & Scripting</a></span>
  </div>
</div>

---

## What you'll learn

- [x] The shape of an IoT system
- [x] Smooth noisy sensor data (tested)
- [x] Messaging with MQTT
- [x] Edge vs cloud processing
- [x] The device + library ecosystem

IoT (Internet of Things) connects physical sensors and devices to software. Python runs across the stack — on the device ([Embedded Python](../embedded/embedded-python.md)), at the edge, and in the cloud. The sensor-processing example here is **run-verified**.

---

## The shape of an IoT system

```
   sensors  →  edge device  →  messaging  →  cloud/backend  →  dashboard
   (temp,      (Raspberry Pi,   (MQTT)        (store, analyze)  (visualize,
    motion)     microcontroller)                                 alert)
```

Data flows from cheap sensors, through a local device that may pre-process it, over a lightweight protocol (usually **MQTT**), to a backend that stores and acts on it.

---

## Smoothing noisy sensor data (tested)

Real sensors are noisy — readings jitter. A **moving average** smooths them, which is one of the most common IoT data tasks. Runnable:

```python
from collections import deque

class MovingAverage:
    def __init__(self, window):
        self.buf = deque(maxlen=window)     # keeps only the last `window` values

    def add(self, x):
        self.buf.append(x)
        return sum(self.buf) / len(self.buf)

ma = MovingAverage(window=3)
print([round(ma.add(v), 2) for v in [10, 20, 30, 40]])
```

Output:

```text
[10.0, 15.0, 20.0, 30.0]
```

The average slides over the last 3 readings: after 40, the window is (20, 30, 40) → 30. Using `deque(maxlen=3)` means old values drop off automatically — an elegant, efficient sliding window. This same pattern smooths temperature, filters spikes, and detects trends on-device.

---

## Messaging with MQTT

**MQTT** is the dominant IoT protocol — lightweight publish/subscribe designed for unreliable networks and tiny devices. A device *publishes* readings to a topic; backends *subscribe*. It's the same pub/sub decoupling as an [event bus](../web/expert/event-driven-architecture.md), tuned for constrained devices.

```python
import paho.mqtt.client as mqtt    # pip install paho-mqtt

client = mqtt.Client()
client.connect("broker.example.com", 1883)

# Device publishes a reading
client.publish("home/livingroom/temp", "21.5")

# Backend subscribes
def on_message(client, userdata, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")

client.subscribe("home/+/temp")     # + is a single-level wildcard
client.on_message = on_message
client.loop_forever()
```

!!! note "MQTT snippet needs paho-mqtt + a broker"
    This follows paho-mqtt's documented API and isn't run-verified here (the moving-average code is). Note the topic wildcard `home/+/temp` — MQTT's hierarchical topics with wildcards make it easy to subscribe to whole categories of devices.

---

## Edge vs cloud

A key IoT design decision is *where* processing happens:

- **Edge (on the device)** — process data locally: smooth it, detect events, act immediately. Lower latency, less bandwidth, works offline. Constrained by the device's CPU/power.
- **Cloud** — send raw data up for heavy analysis, storage, ML, dashboards. More power, but needs connectivity and bandwidth.

Most real systems split the work: the edge filters/aggregates (like our moving average), sending only meaningful data up — saving bandwidth and battery.

---

## The ecosystem

| Layer | Tools |
|---|---|
| Device runtime | MicroPython, CircuitPython, CPython on Pi ([Embedded](../embedded/embedded-python.md)) |
| Messaging | paho-mqtt, MQTT brokers (Mosquitto) |
| Hardware I/O | gpiozero, RPi.GPIO ([Embedded Linux](../embedded/embedded-linux.md)) |
| Backend | FastAPI, time-series DBs (InfluxDB) |
| Dashboards | Grafana, Home Assistant |

---

## Practice exercises

1. Add a `max`/`min` tracker alongside the moving average to flag out-of-range readings.
2. Extend `MovingAverage` to detect a spike (current reading far from the average) and return a flag.
3. Design MQTT topic names for a home with several rooms and sensor types.
4. Explain when you'd process on the edge vs send raw data to the cloud, with a concrete example.
5. Simulate a sensor stream (random walk) and smooth it, printing raw vs smoothed values.
