---
title: "Firmware Testing"
description: Test embedded firmware from Python over serial and other protocols
---

# Firmware Testing <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🔧 Embedded & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisites: <a href="../../testing/pytest/">Testing</a>, <a href="../../core/beginner/file-handling/">File Handling</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Talk to a device over a serial port
- [x] Frame and parse a binary protocol with a checksum
- [x] Build a test harness around real hardware
- [x] Simulate a device so tests run without hardware
- [x] Structure hardware-in-the-loop tests

---

## Why Python for firmware testing

Firmware runs on the device (often in C/C++), but the *tests* that poke it, feed it inputs, and check its responses are frequently written in Python. Python is ideal here: quick to write, great libraries for serial/USB/network, and it plays well with `pytest`. The pattern is **host-side test code driving device-side firmware**.

```
   ┌──────────────┐   serial / USB / network   ┌──────────────┐
   │  Python test  │ ◀──────────────────────▶  │   firmware    │
   │  (host PC)    │   send commands, read      │  (the device) │
   └──────────────┘   responses                 └──────────────┘
```

---

## Talking over serial

The workhorse is **`pyserial`**. Opening a port and exchanging bytes:

```python
import serial   # pip install pyserial

with serial.Serial("COM3", baudrate=115200, timeout=1) as port:
    port.write(b"PING\n")
    response = port.readline()      # reads until newline or timeout
    print(response)                 # e.g. -> b'PONG\n'
```

!!! note "`pyserial` needs the package and a real port"
    This uses `pyserial` against an actual serial device (`COM3` on Windows, `/dev/ttyUSB0` on Linux), so it can't be run-verified here. The **protocol framing/parsing and the simulated device below are pure stdlib and fully tested** — and that's the part most worth getting right.

---

## Framing a binary protocol

Real devices rarely speak plain text. They use **framed binary protocols**: a start byte, a length, a payload, a checksum, an end byte. Framing lets the receiver find message boundaries and detect corruption. Here's a complete, tested implementation:

```python
STX, ETX = 0x02, 0x03      # start/end markers

def build_frame(payload: bytes) -> bytes:
    checksum = 0
    for b in payload:
        checksum ^= b                      # XOR checksum
    return bytes([STX, len(payload)]) + payload + bytes([checksum, ETX])

def parse_frame(frame: bytes) -> bytes:
    if frame[0] != STX or frame[-1] != ETX:
        raise ValueError("bad framing")
    length = frame[1]
    payload = frame[2:2 + length]
    checksum = frame[2 + length]
    calc = 0
    for b in payload:
        calc ^= b
    if calc != checksum:
        raise ValueError(f"checksum mismatch: got {checksum}, want {calc}")
    return payload
```

Building and parsing a frame:

```python
frame = build_frame(b"HELLO")
print("frame bytes:", frame.hex())
print("parsed:", parse_frame(frame))

# Corrupt one payload byte and confirm the checksum catches it
corrupt = bytearray(frame); corrupt[3] ^= 0xFF
parse_frame(bytes(corrupt))
```

Output:

```text
frame bytes: 020548454c4c4f4203
parsed: b'HELLO'
Traceback (most recent call last):
  ...
ValueError: checksum mismatch: got 66, want 189
```

The valid frame round-trips (`HELLO` in, `HELLO` out). Flip a single bit in the payload and the checksum mismatch is caught — exactly the corruption detection a real link needs. Decoding the hex: `02` (start), `05` (length), `48 45 4c 4c 4f` (HELLO), `42` (checksum), `03` (end).

---

## Simulate the device — so tests run without hardware

Hardware-in-the-loop testing is powerful but slow and unavailable in CI. The fix: a **simulator** that speaks the same protocol, so most tests run against fake hardware and only a few run against the real thing.

```python
class SimulatedDevice:
    """A fake device that answers framed commands — no hardware needed."""
    def handle(self, frame: bytes) -> bytes:
        command = parse_frame(frame)
        if command == b"PING":
            return build_frame(b"PONG")
        if command.startswith(b"ECHO:"):
            return build_frame(command[5:])
        return build_frame(b"ERR")

def test_ping_pong():
    device = SimulatedDevice()
    reply = device.handle(build_frame(b"PING"))
    assert parse_frame(reply) == b"PONG"

def test_echo():
    device = SimulatedDevice()
    reply = device.handle(build_frame(b"ECHO:hi"))
    assert parse_frame(reply) == b"hi"
```

Both tests pass with no serial port in sight. The same test *logic* later runs against real hardware by swapping `SimulatedDevice.handle` for a function that writes to and reads from a `pyserial` port — this is the [hexagonal](../web/expert/hexagonal-architecture.md) idea applied to hardware: the test depends on a "device" interface, not on serial specifically.

---

## Structuring hardware-in-the-loop (HIL) tests

A pragmatic firmware test suite has layers:

- **Unit tests** — protocol encode/decode, parsing, state logic. Pure Python, instant, run in CI. (The framing tests above.)
- **Simulated integration** — full command/response flows against `SimulatedDevice`. Fast, run in CI.
- **Hardware-in-the-loop** — the real device on a test bench, driven over serial. Slow, needs the rig, run on a dedicated runner or nightly.

!!! tip "Push logic out of the hardware layer"
    The more of your protocol and behavior you can test without hardware, the faster and more reliable your suite. Reserve real-device tests for what genuinely needs the hardware (timing, electrical behavior, the actual firmware image).

---

## Practice exercises

1. Add a `RESET` command to `SimulatedDevice` that returns `build_frame(b"OK")`, and test it.
2. Change the checksum from XOR to a sum-modulo-256 and update both `build_frame` and `parse_frame`; confirm the round-trip test still passes.
3. Add a `read_frames` generator that, given a stream of bytes, yields complete frames (handling partial reads — the real serial challenge).
4. Write a test that feeds a frame with a wrong length byte and asserts a clear error.
5. Sketch how you'd swap `SimulatedDevice` for a real `pyserial` connection without changing the test logic.
