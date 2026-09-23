---
title: "Python for Robotics"
description: Control, sensing and motion planning with Python and ROS
---

# Python for Robotics <span class="pm-badge pm-badge-advanced">Domain</span>

<div class="pm-topic-header">
  <strong>🌍 Domain Applications</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 weeks</span>
    <span>📚 Prereqs: <a href="../embedded/robotics-middleware.md">Robotics Middleware</a>, <a href="../embedded/real-time-systems.md">Real-time Systems</a></span>
  </div>
</div>

---

## What you'll learn

- [x] The sense-plan-act loop
- [x] A simple control loop (tested — PID)
- [x] Sensing and sensor fusion basics
- [x] Motion planning concepts
- [x] The ROS ecosystem

Robotics combines sensing, decision-making, and physical action. Python is widely used for the higher-level logic (planning, coordination, ML), with real-time control often in C/C++ underneath (see [Real-time Systems](../embedded/real-time-systems.md)). The PID controller here is **run-verified**.

---

## Sense → Plan → Act

Every robot runs a version of this loop:

```
   SENSE            PLAN               ACT
   read sensors  →  decide what to  →  drive motors  →  (repeat many times/sec)
   (camera,         do (avoid the      (wheels,
    lidar, IMU)     obstacle, grab)     arm, gripper)
```

The [Robotics Middleware](../embedded/robotics-middleware.md) page shows how ROS wires these stages together as nodes. Here we focus on the *control* inside the "Act" stage.

---

## A PID controller (tested)

The workhorse of robot control is the **PID controller** — it drives a system toward a target by reacting to the error (how far off you are), summing past error, and anticipating future error. It's how a robot holds a speed, a drone stays level, a thermostat hits a temperature. Runnable pure Python:

```python
class PID:
    def __init__(self, kp, ki, kd):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.integral = 0.0
        self.prev_error = 0.0

    def update(self, target, measured, dt):
        error = target - measured
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt
        self.prev_error = error
        return self.kp * error + self.ki * self.integral + self.kd * derivative

# Drive a value from 0 toward a target of 10
pid = PID(kp=0.5, ki=0.1, kd=0.05)
value = 0.0
for _ in range(20):
    control = pid.update(target=10.0, measured=value, dt=0.1)
    value += control            # apply the control effort (simplified plant)
print(f"{value:.2f}")
```

Output:

```text
10.29
```

Starting from 0, the controller drives the value to ~10.29 — it reached the target of 10 and slightly overshot, which is exactly the kind of behavior PID tuning manages. The three terms balance responsiveness and stability: **P** reacts to current error, **I** eliminates steady-state offset, **D** damps overshoot. Tuning `kp/ki/kd` to minimize that overshoot while staying responsive is the art of control engineering.

---

## Sensing and fusion

- **Sensors** — cameras, LIDAR (distance), IMU (orientation/acceleration), encoders (wheel rotation), each noisy and partial.
- **Sensor fusion** — combining multiple noisy sensors into a better estimate than any alone. The classic tool is the **Kalman filter**, which fuses predictions with measurements weighted by their uncertainty. Libraries: `filterpy`, NumPy.
- **Perception** — turning raw sensor data into meaning (detecting objects, mapping the environment), increasingly ML-based.

---

## Motion planning

Getting from A to B without hitting things:

- **Path planning** — algorithms like A* (see the Algorithms section), RRT, and Dijkstra find routes through space.
- **Obstacle avoidance** — reactive adjustments as new obstacles appear.
- **Kinematics** — the math relating joint angles to end-effector position (for arms).

These often build on graph algorithms and geometry — general CS skills applied to physical space.

---

## The ROS ecosystem

!!! note "ROS/robotics libraries follow documented APIs"
    ROS 2 (`rclpy`), and robotics libraries aren't installed here, so those references are documented rather than run-verified. The PID controller above **is** run-verified, since control logic is pure math.

| Need | Tool |
|---|---|
| Middleware / integration | ROS 2 ([Robotics Middleware](../embedded/robotics-middleware.md)) |
| Simulation | Gazebo, PyBullet, MuJoCo |
| Sensor fusion | filterpy, NumPy |
| Perception / ML | OpenCV, PyTorch |
| Motion planning | MoveIt, OMPL, networkx |

---

## Practice exercises

1. Tune the PID gains — try `kp` only, then add `ki`, then `kd` — and observe overshoot/settling.
2. Add a simulated disturbance (subtract a constant each step) and see the integral term compensate.
3. Implement a simple proportional-only controller and explain why it leaves steady-state error.
4. Sketch the sense-plan-act loop for a robot vacuum avoiding obstacles.
5. Explain what a Kalman filter adds over just averaging two sensors.
