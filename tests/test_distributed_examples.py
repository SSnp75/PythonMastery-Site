"""Tests for the runnable code examples used in the Distributed Systems docs.

These mirror the examples shown on the site so CI fails if an example breaks.
Pure standard library — no external services required.
"""
from __future__ import annotations
import hashlib
from dataclasses import dataclass
from typing import Callable


# --------------------------------------------------------------------------
# CRDTs (docs/distributed/crdts.md)
# --------------------------------------------------------------------------
class GCounter:
    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        self.counts: dict[str, int] = {}

    def increment(self, n: int = 1) -> None:
        self.counts[self.node_id] = self.counts.get(self.node_id, 0) + n

    def value(self) -> int:
        return sum(self.counts.values())

    def merge(self, other: "GCounter") -> None:
        for node, cnt in other.counts.items():
            self.counts[node] = max(self.counts.get(node, 0), cnt)


def test_gcounter_converges():
    a, b = GCounter("A"), GCounter("B")
    a.increment(3)
    b.increment(5)
    a.merge(b)
    b.merge(a)
    assert a.value() == b.value() == 8


def test_gcounter_merge_idempotent():
    a, b = GCounter("A"), GCounter("B")
    a.increment(3)
    b.increment(5)
    a.merge(b)
    a.merge(b)  # merging again changes nothing
    assert a.value() == 8


@dataclass
class LWWRegister:
    value: str = ""
    timestamp: float = 0.0

    def set(self, value: str, ts: float) -> None:
        if ts > self.timestamp:
            self.value, self.timestamp = value, ts

    def merge(self, other: "LWWRegister") -> None:
        if other.timestamp > self.timestamp:
            self.value, self.timestamp = other.value, other.timestamp


def test_lww_register_latest_wins():
    r1, r2 = LWWRegister(), LWWRegister()
    r1.set("red", ts=10.0)
    r2.set("blue", ts=12.0)
    r1.merge(r2)
    r2.merge(r1)
    assert r1.value == r2.value == "blue"


# --------------------------------------------------------------------------
# Consistent hashing (docs/distributed/caching.md)
# --------------------------------------------------------------------------
class HashRing:
    def __init__(self, nodes: list[str], vnodes: int = 100) -> None:
        self.vnodes = vnodes
        self.ring: dict[int, str] = {}
        for n in nodes:
            self._add(n)
        self.sorted_keys = sorted(self.ring)

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def _add(self, node: str) -> None:
        for i in range(self.vnodes):
            self.ring[self._hash(f"{node}:{i}")] = node

    def get_node(self, key: str) -> str:
        h = self._hash(key)
        for k in self.sorted_keys:
            if h <= k:
                return self.ring[k]
        return self.ring[self.sorted_keys[0]]


def test_hashring_is_deterministic():
    ring = HashRing(["cache1", "cache2", "cache3"])
    keys = [f"user:{i}" for i in range(50)]
    first = {k: ring.get_node(k) for k in keys}
    # same ring, same keys -> identical placement
    ring2 = HashRing(["cache1", "cache2", "cache3"])
    assert all(ring2.get_node(k) == first[k] for k in keys)


def test_hashring_minimizes_movement():
    keys = [f"user:{i}" for i in range(1000)]
    before = {k: HashRing(["cache1", "cache2", "cache3"]).get_node(k) for k in keys}
    ring2 = HashRing(["cache1", "cache2", "cache3", "cache4"])
    after = {k: ring2.get_node(k) for k in keys}
    moved = sum(1 for k in keys if before[k] != after[k])
    # far less than naive modulo (~75%); consistent hashing keeps it well below half
    assert moved < 500


# --------------------------------------------------------------------------
# Event sourcing (docs/distributed/event-sourcing-cqrs.md)
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Deposited:
    amount: int


@dataclass(frozen=True)
class Withdrawn:
    amount: int


class Account:
    def __init__(self) -> None:
        self.balance = 0

    def apply(self, event) -> None:
        if isinstance(event, Deposited):
            self.balance += event.amount
        elif isinstance(event, Withdrawn):
            self.balance -= event.amount


def test_event_replay_rebuilds_state():
    log = [Deposited(100), Withdrawn(30), Deposited(50), Withdrawn(20)]
    acct = Account()
    for e in log:
        acct.apply(e)
    assert acct.balance == 100


# --------------------------------------------------------------------------
# Raft voting (docs/distributed/raft.md)
# --------------------------------------------------------------------------
def has_majority(votes: int, cluster_size: int) -> bool:
    return votes > cluster_size // 2


def test_majority():
    assert has_majority(3, 5) is True
    assert has_majority(2, 5) is False
    assert has_majority(2, 3) is True


@dataclass
class RaftNode:
    node_id: str
    current_term: int = 0
    voted_for: str | None = None

    def request_vote(self, candidate: str, term: int) -> bool:
        if term < self.current_term:
            return False
        if term > self.current_term:
            self.current_term = term
            self.voted_for = None
        if self.voted_for in (None, candidate):
            self.voted_for = candidate
            return True
        return False


def test_raft_one_vote_per_term():
    n = RaftNode("f")
    assert n.request_vote("A", term=1) is True
    assert n.request_vote("B", term=1) is False   # already voted this term
    assert n.request_vote("B", term=2) is True     # new term
    assert n.current_term == 2 and n.voted_for == "B"


# --------------------------------------------------------------------------
# Saga with compensation (docs/distributed/saga.md)
# --------------------------------------------------------------------------
@dataclass
class Step:
    name: str
    action: Callable[[], None]
    compensate: Callable[[], None]


class Saga:
    def __init__(self) -> None:
        self.steps: list[Step] = []

    def add(self, name, action, compensate) -> None:
        self.steps.append(Step(name, action, compensate))

    def execute(self) -> dict:
        completed: list[Step] = []
        try:
            for step in self.steps:
                step.action()
                completed.append(step)
            return {"status": "committed", "completed": [s.name for s in completed]}
        except Exception as e:  # noqa: BLE001 - intentional in saga runner
            for step in reversed(completed):
                step.compensate()
            return {"status": "aborted", "reason": str(e),
                    "compensated": [s.name for s in reversed(completed)]}


def _step_fns(log: list[str], name: str, fail: bool = False):
    def action():
        if fail:
            raise RuntimeError(f"{name} failed")
        log.append(f"do:{name}")

    def compensate():
        log.append(f"undo:{name}")

    return action, compensate


def test_saga_happy_path():
    log: list[str] = []
    saga = Saga()
    for name in ["reserve_stock", "charge_card", "ship_order"]:
        saga.add(name, *_step_fns(log, name))
    result = saga.execute()
    assert result["status"] == "committed"
    assert log == ["do:reserve_stock", "do:charge_card", "do:ship_order"]


def test_saga_compensates_in_reverse_on_failure():
    log: list[str] = []
    saga = Saga()
    saga.add("reserve_stock", *_step_fns(log, "reserve_stock"))
    saga.add("charge_card", *_step_fns(log, "charge_card"))
    saga.add("ship_order", *_step_fns(log, "ship_order", fail=True))
    result = saga.execute()
    assert result["status"] == "aborted"
    assert log == ["do:reserve_stock", "do:charge_card",
                   "undo:charge_card", "undo:reserve_stock"]
