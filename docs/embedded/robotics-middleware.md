---
title: "Robotics Middleware"
description: Build robot software with ROS 2 — nodes, topics, services and Python
---

# Robotics Middleware <span class="pm-badge pm-badge-advanced">Advanced</span>

<div class="pm-topic-header">
  <strong>🔧 Embedded & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="../../web/expert/event-driven-architecture/">Event-driven Architecture</a>, <a href="../../systems/proficient/asyncio/">Asyncio</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What robotics middleware solves
- [x] ROS 2 nodes, topics, and the pub/sub model
- [x] Write publisher and subscriber nodes in Python (`rclpy`)
- [x] Services vs topics
- [x] How sensors, control, and actuators connect

!!! note "This topic requires a ROS 2 installation"
    The examples use ROS 2's Python client library `rclpy`, which needs a ROS 2 distribution installed (Humble, Jazzy, etc.) and isn't part of standard Python — so they aren't run-verified here. They follow the documented `rclpy` API. The *concepts* (nodes, pub/sub) mirror the tested event-bus from [Event-driven Architecture](../web/expert/event-driven-architecture.md).

---

## The problem middleware solves

A robot is many components that must cooperate: cameras, LIDAR, motors, a planner, a controller. Wiring them together directly — each part knowing about every other — is unmanageable. **Robotics middleware** provides the plumbing: a standard way for components to find each other and exchange messages, so you build the robot from independent, reusable pieces.

**ROS (Robot Operating System)** — really a middleware and toolset, not an OS — is the dominant framework. **ROS 2** is the modern version (production-ready, real-time-friendly, no central master). Its core abstraction is a graph of **nodes** that communicate over **topics**.

```
        ┌─────────────────── ROS 2 graph ───────────────────┐
        │                                                     │
   [camera node] ──/image──▶ [detector node] ──/objects──▶ [planner node]
        │                                                     │
   [lidar node]  ──/scan───▶ [ ... ]         /cmd_vel──▶ [motor node]
        └─────────────────────────────────────────────────────┘
             nodes publish/subscribe to named topics
```

---

## Nodes, topics, and pub/sub

- **Node** — an independent process doing one job (read the camera, plan a path, drive the motors).
- **Topic** — a named channel (`/scan`, `/cmd_vel`) carrying a stream of typed messages.
- **Publisher / Subscriber** — a node *publishes* to a topic; any node *subscribes* to receive. Publishers and subscribers don't know about each other — exactly the decoupling of an event bus, distributed across processes.

This is publish/subscribe, the same pattern as [Event-driven Architecture](../web/expert/event-driven-architecture.md) — a node announces data on a topic and moves on; interested nodes react.

---

## A publisher node

`rclpy` is ROS 2's Python client library. A node that publishes a counter every second:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class TalkerNode(Node):
    def __init__(self):
        super().__init__("talker")
        self.pub = self.create_publisher(String, "chatter", 10)
        self.count = 0
        self.create_timer(1.0, self.tick)      # call tick() every 1s

    def tick(self):
        msg = String()
        msg.data = f"hello {self.count}"
        self.pub.publish(msg)
        self.get_logger().info(f"publishing: {msg.data}")
        self.count += 1

def main():
    rclpy.init()
    rclpy.spin(TalkerNode())       # process callbacks until shutdown
    rclpy.shutdown()
```

## A subscriber node

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class ListenerNode(Node):
    def __init__(self):
        super().__init__("listener")
        self.create_subscription(String, "chatter", self.on_message, 10)

    def on_message(self, msg):
        self.get_logger().info(f"received: {msg.data}")

def main():
    rclpy.init()
    rclpy.spin(ListenerNode())
    rclpy.shutdown()
```

Run both (in separate terminals) and the listener prints each message the talker sends — `received: hello 0`, `received: hello 1`, … — even though neither node references the other. They meet only through the `chatter` topic. The `10` argument is the **queue depth** (how many messages to buffer).

---

## Topics vs services vs actions

ROS 2 offers three communication styles for different needs:

| Mechanism | Style | Use for |
|---|---|---|
| **Topic** | One-way stream (pub/sub) | Continuous data: sensor readings, velocity commands |
| **Service** | Request/response (like a function call) | One-off queries: "what's the battery level?" |
| **Action** | Long-running goal with feedback | Tasks that take time: "navigate to X", with progress + cancel |

Rule of thumb: **topics** for streams, **services** for quick request/reply, **actions** for goals that take time and need feedback or cancellation.

---

## How it fits a real robot

A typical robot software stack layers these pieces:

```
   Sensors → perception → planning → control → actuators
   (/scan,    (detect      (path      (/cmd_vel) (motors,
    /image)    objects)     planning)             servos)
```

Each stage is one or more nodes exchanging messages on topics. ROS 2 also brings a rich toolset: `rviz` (3D visualization), `ros2 bag` (record/replay all messages — invaluable for debugging and testing offline), simulation via Gazebo, and coordinate-frame tracking (`tf2`). The [Hardware Simulation](hardware-simulation.md) idea applies here: develop and test against a simulated robot, then deploy to the real one.

!!! tip "Record everything with `ros2 bag`"
    Because all communication flows through topics, you can record the entire message stream and replay it later. That turns a hard-to-reproduce field bug into a repeatable test — one of ROS's biggest practical wins.

---

## Practice exercises

1. Modify the talker to publish a `sensor_msgs/Temperature` message instead of a string.
2. Write a node that subscribes to `chatter` and republishes an uppercased version to a new topic — a simple processing node.
3. Sketch (in words or code) a ROS 2 **service** that returns a robot's battery percentage on request.
4. Explain why pub/sub decoupling lets you swap the camera node for a simulated one without touching the detector node.
5. Describe how you'd use `ros2 bag` to debug a navigation failure that only happens outdoors.
