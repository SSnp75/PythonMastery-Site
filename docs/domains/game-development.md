---
title: "Python for Game Development"
description: Build games with Pygame — game loops, input, and simple physics
---

# Python for Game Development <span class="pm-badge pm-badge-competent">Domain</span>

<div class="pm-topic-header">
  <strong>🌍 Domain Applications</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prereqs: <a href="../core/competent/oop-fundamentals.md">OOP Fundamentals</a></span>
  </div>
</div>

---

## What you'll learn

- [x] The game loop — the heart of every game
- [x] Fixed-timestep updates and simple physics (tested)
- [x] Input handling and game state
- [x] Pygame basics
- [x] Where to go beyond Pygame

Games are a fun, motivating way to practice OOP, state management, and real-time loops. The physics logic here is **run-verified**; the Pygame rendering follows its documented API.

---

## The game loop

Every game runs the same fundamental loop, forever, many times per second:

```
   while running:
       1. handle input   (keys, mouse, quit)
       2. update state    (move things, physics, collisions)
       3. render          (draw the current frame)
       4. wait            (cap the frame rate)
```

Everything — a platformer, a puzzle, a shooter — is variations on this loop. Understanding it is 80% of game programming.

---

## Physics with a fixed timestep (tested)

The "update" phase advances the simulation by a time delta (`dt`). Here's gravity acting on a falling object — pure Python, runnable:

```python
def simulate(steps, dt, gravity=9.8):
    y, vy = 100.0, 0.0                # start at height 100, zero velocity
    positions = []
    for _ in range(steps):
        vy -= gravity * dt            # gravity accelerates downward
        y += vy * dt                  # velocity moves position
        positions.append(round(y, 2))
    return positions

print(simulate(3, 0.1))
```

Output:

```text
[99.9, 99.71, 99.41]
```

Each step the object falls a little faster (velocity accumulates), so the gaps between positions grow — that's acceleration. Using a fixed `dt` keeps the physics **deterministic and frame-rate independent**, the standard approach in real games (a variable timestep makes physics wobble when the frame rate dips).

---

## Pygame basics

**Pygame** is the classic Python game library. The loop in Pygame form:

```python
import pygame     # pip install pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

x, y = 400, 300
running = True
while running:
    for event in pygame.event.get():          # 1. input
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  x -= 5            # 2. update
    if keys[pygame.K_RIGHT]: x += 5

    screen.fill((0, 0, 0))                     # 3. render
    pygame.draw.circle(screen, (255, 0, 0), (x, y), 20)
    pygame.display.flip()

    clock.tick(60)                             # 4. cap at 60 FPS
pygame.quit()
```

!!! note "Pygame needs the library and a display"
    Pygame isn't installed here and needs a window, so this follows its documented API rather than being run-verified. Notice it's exactly the four-phase loop above — input, update, render, wait. The physics `simulate` example *is* run-verified.

---

## Core concepts beyond the loop

- **Sprites** — game objects with position, image, and behavior (a natural fit for OOP classes).
- **Collision detection** — do two rectangles/circles overlap? Pygame has helpers (`Rect.colliderect`).
- **Game state** — menu vs playing vs game-over; often a simple state machine.
- **Delta time** — multiply movement by `dt` so speed is consistent regardless of frame rate.

---

## The ecosystem

| Need | Tool |
|---|---|
| 2D games, learning | **Pygame** (the standard starting point) |
| Higher-level 2D | Arcade, pyglet |
| Full engines w/ Python | Godot (GDScript/Python-like), Panda3D (3D) |
| Web/mobile export | Pygame is limited here; consider a dedicated engine |

Python isn't the choice for AAA games (that's C++/C#), but it's excellent for learning game programming, prototyping, game jams, and 2D indie games.

---

## Practice exercises

1. Extend `simulate` to bounce: when `y` hits 0, reverse and dampen the velocity (`vy = -vy * 0.8`).
2. Add horizontal motion with its own velocity and simulate a projectile arc.
3. Write a pure-Python collision check: do two axis-aligned rectangles overlap?
4. Sketch a state machine for menu → playing → paused → game-over transitions.
5. Build the classic beginner game (Pong or Snake) in Pygame using the four-phase loop.
