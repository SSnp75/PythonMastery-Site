---
title: "Desktop Automation"
description: Control the mouse, keyboard and screen with PyAutoGUI
---

# Desktop Automation <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🤖 Automation Track</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 days</span>
    <span>📚 Prereqs: Automation & Scripting</span>
  </div>
</div>

---

## What you'll learn

- [x] Control the mouse (move, click, drag)
- [x] Type text and press key combinations
- [x] Take screenshots and locate images on screen
- [x] Read screen contents with pixel/OCR techniques
- [x] Understand the cross-platform pitfalls
- [x] Automate safely with fail-safes

Desktop automation drives the graphical interface the way a human would — moving the pointer, clicking buttons, typing. It's the tool of last resort for apps that have **no API, no CLI, and no scriptable interface**. When those exist, prefer them; GUI automation is inherently fragile.

!!! warning "These examples need a real display"
    The code here requires `pyautogui` (plus a screen/keyboard). It cannot run on a headless server or in CI without a virtual display. Install with:
    ```bash
    pip install pyautogui
    ```
    On Linux you also need `scrot` and X11; on macOS you must grant Accessibility permissions.

---

## 1. The fail-safe (read this first)

Before writing any automation, know how to stop it. A runaway script that's clicking and typing on its own can be hard to interrupt.

```python
import pyautogui

# FAIL-SAFE: slam the mouse into any screen corner to abort the script.
pyautogui.FAILSAFE = True    # this is on by default — leave it on

# Add a small pause after every call so you can watch (and interrupt) it.
pyautogui.PAUSE = 0.5        # seconds between actions
```

!!! danger "Always keep the fail-safe enabled"
    With `FAILSAFE = True`, jerking the mouse to a corner raises `FailSafeException` and stops everything. It's your emergency brake. Disabling it means a buggy loop can lock up your session.

---

## 2. Mouse control

```python
import pyautogui

# Where is the mouse, and how big is the screen?
width, height = pyautogui.size()      # e.g. (1920, 1080)
x, y = pyautogui.position()           # current cursor position

# Move the cursor (absolute coordinates, top-left is 0,0)
pyautogui.moveTo(500, 300, duration=0.5)   # glide over 0.5s

# Move relative to current position
pyautogui.moveRel(100, 0, duration=0.25)   # 100px to the right

# Clicks
pyautogui.click(500, 300)                  # move + left-click
pyautogui.click(clicks=2, interval=0.1)    # double-click here
pyautogui.rightClick()
pyautogui.click(button="middle")

# Drag (e.g. drag-and-drop)
pyautogui.dragTo(800, 600, duration=1, button="left")

# Scroll (positive = up, negative = down)
pyautogui.scroll(-300)
```

**Coordinate system:** `(0, 0)` is the top-left of the primary screen; x grows rightward, y grows *downward*. The `duration` argument makes moves visible and more reliable — instant jumps can be missed by some UIs.

---

## 3. Keyboard control

```python
import pyautogui

# Type a string (interval spaces out the keystrokes)
pyautogui.write("Hello, world!", interval=0.05)

# Press a single key
pyautogui.press("enter")
pyautogui.press("tab")

# Press several keys in sequence
pyautogui.press(["h", "i"])

# Hotkey combinations (keys pressed together, released in reverse)
pyautogui.hotkey("ctrl", "c")        # copy
pyautogui.hotkey("ctrl", "v")        # paste
pyautogui.hotkey("alt", "tab")       # switch window

# Hold a key down for a block of actions
with pyautogui.hold("shift"):
    pyautogui.press(["left", "left", "left"])   # select 3 chars left
```

!!! tip "`write` is for text, `press`/`hotkey` are for keys"
    Use `write()` for literal characters you want typed. Use `press()` for named keys (enter, tab, f5) and `hotkey()` for combos like Ctrl+S. Trying to `write("enter")` types the word "enter", not the Enter key.

---

## 4. Screenshots & finding things on screen

```python
import pyautogui

# Capture the whole screen → a Pillow Image
screenshot = pyautogui.screenshot()
screenshot.save("screen.png")

# Capture a region: (left, top, width, height)
region = pyautogui.screenshot(region=(0, 0, 400, 300))

# Read a single pixel's colour
r, g, b = pyautogui.pixel(100, 200)

# Check whether a pixel matches an expected colour (with tolerance)
matches = pyautogui.pixelMatchesColor(100, 200, (255, 0, 0), tolerance=10)
```

### Locating an image (template matching)

Instead of hard-coding coordinates, find a button by its picture. This survives windows moving around.

```python
import pyautogui

# Find where 'button.png' appears on screen; None if not found
location = pyautogui.locateOnScreen("button.png", confidence=0.9)

if location is not None:
    center = pyautogui.center(location)   # Point(x, y)
    pyautogui.click(center)
else:
    print("Button not found on screen")
```

!!! note "`confidence` needs OpenCV"
    The `confidence` argument (fuzzy matching, 0–1) requires `opencv-python` installed. Without it, matching is exact and brittle — a single pixel difference means no match.

**Reading text (OCR):** PyAutoGUI can capture the screen, but it can't read text. For that, pair it with **Tesseract** via `pytesseract`:

```python
import pyautogui
import pytesseract   # pip install pytesseract, plus the Tesseract binary

image = pyautogui.screenshot(region=(0, 0, 400, 100))
text = pytesseract.image_to_string(image)
```

---

## 5. A complete example: automate a repetitive form

```python
import pyautogui
import time

pyautogui.PAUSE = 0.4
pyautogui.FAILSAFE = True

def fill_form(entries: list[dict]) -> int:
    """Type each record into a form, tabbing between fields and submitting.

    Assumes the form's first field is already focused.
    Returns the number of records entered.
    """
    for i, record in enumerate(entries, start=1):
        pyautogui.write(record["name"], interval=0.02)
        pyautogui.press("tab")
        pyautogui.write(record["email"], interval=0.02)
        pyautogui.press("tab")
        pyautogui.press("enter")          # submit
        time.sleep(1)                     # wait for the form to reset
    return len(entries)

# data = [{"name": "Alice", "email": "a@x.com"}, ...]
# fill_form(data) -> 2
```

This works, but notice how much it *assumes*: which field has focus, that Tab moves in the right order, that the form resets in one second. That fragility is the defining trait of desktop automation.

---

## 6. Cross-platform caveats

| Concern | Windows | macOS | Linux |
|---|---|---|---|
| Extra setup | none | grant **Accessibility** permission | needs X11 + `scrot` |
| Wayland (Linux) | n/a | n/a | **not supported** — must use X11 |
| Screen scaling | high-DPI can offset coordinates | Retina doubles coordinates | varies |
| Multi-monitor | primary screen only by default | same | same |

**Other gotchas that bite everyone:**

- **Coordinates are brittle.** A different screen resolution, window position, or DPI setting breaks hard-coded `(x, y)` values. Prefer `locateOnScreen` over fixed coordinates.
- **Timing is a guess.** `time.sleep()` waits a fixed amount; if the app is slow that day, your script clicks too early. There's no reliable "wait until ready" like browser tools have.
- **It steals your input.** While the script runs, it controls the real mouse and keyboard — you can't use the computer for anything else.

---

## When NOT to use desktop automation

Reach for a better tool if one exists:

- The app has an **API or SDK** → call it directly.
- It's a **website** → use [Browser Automation](browser.md) (far more robust).
- It's a **command-line program** → use `subprocess` (see [Automation & Scripting](scripting.md)).
- You need to **process files** → use `pathlib`/`shutil`, no GUI needed.

Desktop automation is the fallback when a legacy or closed application offers no other way in.

---

## Alternatives worth knowing

- **`pynput`** — lower-level mouse/keyboard control, and it can *listen* for input events (useful for building macro recorders).
- **`pywinauto`** (Windows) — automates via the Windows UI Automation API, targeting controls by name/type instead of pixel coordinates. Much sturdier than PyAutoGUI for Windows desktop apps.
- **AutoHotkey** — not Python, but often the pragmatic choice for Windows-only macros.

---

## Practice exercises

1. Write a script that takes a screenshot every 10 seconds for 2 minutes, saving each with a timestamped filename. (Combine with `pathlib` from the scripting topic.)
2. Build a "jiggler" that nudges the mouse 1px every 4 minutes to keep a session awake — with the fail-safe on so you can stop it.
3. Use `locateOnScreen` to find an icon and click it, printing a clear message if it isn't found.
4. Explain in your own notes why `locateOnScreen` is more robust than `click(x, y)`, and when you'd still be forced to use fixed coordinates.
