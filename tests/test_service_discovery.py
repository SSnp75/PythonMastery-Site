"""Tests for the Service Discovery example (docs/distributed/service-discovery.md)."""
from __future__ import annotations
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
        self._rr: dict[str, int] = {}

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
                    i.healthy = False

    def healthy_instances(self, service: str) -> list[Instance]:
        return [i for i in self._services.get(service, []) if i.healthy]

    def discover(self, service: str) -> Instance | None:
        healthy = self.healthy_instances(service)
        if not healthy:
            return None
        idx = self._rr.get(service, 0) % len(healthy)
        self._rr[service] = idx + 1
        return healthy[idx]


def _registry_with_three():
    reg = Registry()
    for addr in ["10.0.0.1:8000", "10.0.0.2:8000", "10.0.0.3:8000"]:
        reg.register("api", addr)
        reg.heartbeat("api", addr, now=100.0)
    return reg


def test_round_robin_load_balancing():
    reg = _registry_with_three()
    picks = [reg.discover("api").address for _ in range(6)]
    assert picks == [
        "10.0.0.1:8000", "10.0.0.2:8000", "10.0.0.3:8000",
        "10.0.0.1:8000", "10.0.0.2:8000", "10.0.0.3:8000",
    ]


def test_unhealthy_instance_expires():
    reg = _registry_with_three()
    # only 1 and 3 keep heartbeating; 2 goes stale
    reg.heartbeat("api", "10.0.0.1:8000", now=200.0)
    reg.heartbeat("api", "10.0.0.3:8000", now=200.0)
    reg.expire(now=200.0, ttl=30.0)
    healthy = sorted(i.address for i in reg.healthy_instances("api"))
    assert healthy == ["10.0.0.1:8000", "10.0.0.3:8000"]


def test_no_healthy_instances_returns_none():
    reg = Registry()
    assert reg.discover("missing") is None
