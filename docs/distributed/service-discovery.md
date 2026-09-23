---
title: "Service Discovery"
description: How services find each other — registries, health checks and client-side load balancing
---

# Service Discovery <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🌐 Distributed Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisites: <a href="../web/expert/microservices/">Microservices</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Why hard-coded addresses break in the cloud
- [x] Service registries and how instances register
- [x] Health checks and TTL-based expiry
- [x] Client-side vs server-side discovery
- [x] Build a registry with round-robin load balancing

---

## The problem: addresses aren't stable

In a static world you'd configure "the payment service is at `10.0.0.5:8000`" and be done. In a cloud/microservices world that breaks constantly: instances **scale up and down**, get **replaced** on deploy, **move** between hosts, and **crash and restart** with new addresses. Hard-coding addresses — or even a fixed list — means constant reconfiguration and broken calls.

**Service discovery** solves this: services **register** themselves in a central **registry** when they start, and callers **look up** the current healthy instances by *name* ("payment-service") rather than address.

```
   startup:   [instance] ──register("api", 10.0.0.7:8000)──▶ [ registry ]
   lookup:    [caller]   ──discover("api")──▶ registry ──▶ 10.0.0.7:8000
   crash:     stops sending heartbeats ──▶ registry marks it unhealthy, drops it
```

---

## A service registry

At its core a registry maps service names to healthy instances. Instances register on startup and send periodic **heartbeats**; if the heartbeats stop, the registry expires the instance. Fully runnable:

```python
from dataclasses import dataclass

@dataclass
class Instance:
    service: str
    address: str
    healthy: bool = True
    last_heartbeat: float = 0.0

class Registry:
    def __init__(self) -> None:
        self._services: dict[str, list[Instance]] = {}
        self._rr: dict[str, int] = {}          # round-robin cursor per service

    def register(self, service: str, address: str) -> None:
        self._services.setdefault(service, [])
        if not any(i.address == address for i in self._services[service]):
            self._services[service].append(Instance(service, address))

    def heartbeat(self, service: str, address: str, now: float) -> None:
        for i in self._services.get(service, []):
            if i.address == address:
                i.last_heartbeat = now
                i.healthy = True

    def expire(self, now: float, ttl: float) -> None:
        for lst in self._services.values():
            for i in lst:
                if now - i.last_heartbeat > ttl:
                    i.healthy = False           # missed heartbeats → unhealthy

    def healthy_instances(self, service: str) -> list[Instance]:
        return [i for i in self._services.get(service, []) if i.healthy]

    def discover(self, service: str) -> Instance | None:
        healthy = self.healthy_instances(service)
        if not healthy:
            return None
        idx = self._rr.get(service, 0) % len(healthy)   # round-robin pick
        self._rr[service] = idx + 1
        return healthy[idx]
```

### Registering and discovering with load balancing

Three API instances register and heartbeat; callers discover them round-robin:

```python
reg = Registry()
for addr in ["10.0.0.1:8000", "10.0.0.2:8000", "10.0.0.3:8000"]:
    reg.register("api", addr)
    reg.heartbeat("api", addr, now=100.0)

picks = [reg.discover("api").address for _ in range(6)]
print("round-robin picks:", picks)
```

Output:

```text
round-robin picks: ['10.0.0.1:8000', '10.0.0.2:8000', '10.0.0.3:8000', '10.0.0.1:8000', '10.0.0.2:8000', '10.0.0.3:8000']
```

`discover` cycles through the healthy instances, spreading load evenly — that's **client-side load balancing** built right into discovery. Six lookups distribute across the three instances twice each.

### Health checks remove dead instances

When an instance stops sending heartbeats, the registry expires it so callers stop being routed to it:

```python
# only instances 1 and 3 keep heartbeating at t=200
reg.heartbeat("api", "10.0.0.1:8000", now=200.0)
reg.heartbeat("api", "10.0.0.3:8000", now=200.0)
# instance 2's last heartbeat was t=100 → now stale
reg.expire(now=200.0, ttl=30.0)

healthy = sorted(i.address for i in reg.healthy_instances("api"))
print("healthy after expiry:", healthy)
```

Output:

```text
healthy after expiry: ['10.0.0.1:8000', '10.0.0.3:8000']
```

Instance 2 hadn't heartbeated since t=100, so with a 30s TTL it's marked unhealthy at t=200 and dropped from the healthy set — future `discover` calls will never return it. This is the self-healing property: crashed instances silently fall out of rotation without anyone reconfiguring anything.

!!! note "Heartbeat TTL is a tradeoff"
    A short TTL detects failures fast but risks dropping a healthy instance that had a brief hiccup; a long TTL is forgiving but keeps routing to dead instances longer. Real systems tune this and often combine passive heartbeats with active health-check probes (the registry calls a `/health` endpoint).

---

## Client-side vs server-side discovery

Two architectures for *where* the discovery/load-balancing happens:

| | **Client-side** | **Server-side** |
|---|---|---|
| Who picks the instance | The caller queries the registry and chooses | A load balancer / proxy in front does it |
| Example | Netflix Eureka + Ribbon; our `discover()` above | Kubernetes Services, AWS ELB, an API gateway |
| Pros | No extra hop; flexible client logic | Clients stay simple; central control |
| Cons | Every client needs discovery logic | Extra network hop; the LB is a dependency |

- **Client-side** — the caller asks the registry for instances and load-balances itself (what our `discover` does). Efficient, but every service must embed the logic.
- **Server-side** — callers hit a stable virtual address; a load balancer routes to a live instance. Simpler clients; this is what **Kubernetes** does with Services (a stable ClusterIP in front of changing pods).

---

## Real-world tools

You rarely build a registry yourself — you use one:

- **Consul** — service registry + health checks + KV store (HashiCorp).
- **etcd** — the consistent store (built on [Raft](raft.md)) behind Kubernetes; also usable directly.
- **Kubernetes Services + DNS** — the most common modern setup: pods register implicitly, and you reach a service by DNS name (`payment-service.default.svc`), with kube-proxy load-balancing to healthy pods.
- **ZooKeeper** — older but still used for coordination and discovery.

Note the theme: registries themselves must be highly available and consistent, so they're typically backed by a consensus system ([Raft](raft.md)/[Paxos](paxos.md)) — discovery sits on top of the consensus foundation.

---

## Practice exercises

1. Add a `deregister` method for graceful shutdown (an instance removes itself), and confirm it's excluded from `discover` immediately.
2. Swap round-robin for **random** selection, and for **least-connections** (track an active-request count per instance).
3. Add weights so a bigger instance receives proportionally more traffic.
4. Simulate a flapping instance (heartbeats, misses, recovers) and verify it re-enters rotation on the next heartbeat.
5. Explain the tradeoff of a 5s vs 60s heartbeat TTL, and when you'd choose each.
