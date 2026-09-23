"""Tests for runnable examples in the concurrency, performance, security and data docs.

Mirrors the site examples so CI fails if one breaks. Standard library only.
"""
from __future__ import annotations
import math


# ==========================================================================
# Concurrency (docs/systems/proficient/)
# ==========================================================================
def test_actor_mailbox():
    import queue, threading
    class Actor:
        def __init__(self):
            self.inbox = queue.Queue()
            self.state = 0
            self._run = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()
        def send(self, msg): self.inbox.put(msg)
        def _loop(self):
            while self._run:
                msg = self.inbox.get()
                if msg == "STOP":
                    self._run = False
                elif isinstance(msg, tuple) and msg[0] == "add":
                    self.state += msg[1]
                self.inbox.task_done()
    a = Actor()
    for i in [1, 2, 3, 4]:
        a.send(("add", i))
    a.inbox.join()
    assert a.state == 10
    a.send("STOP")


def test_futures_map():
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as ex:
        assert list(ex.map(lambda x: x * x, range(6))) == [0, 1, 4, 9, 16, 25]


def test_cooperative_scheduler():
    def task(name, n, log):
        for i in range(n):
            log.append(f"{name}:{i}")
            yield
    def run(tasks):
        log, active = [], list(tasks)
        while active:
            nxt = []
            for t in active:
                try:
                    next(t); nxt.append(t)
                except StopIteration:
                    pass
            active = nxt
        return log
    log = []
    run([task("A", 2, log), task("B", 3, log)])
    assert log == ["A:0", "B:0", "A:1", "B:1", "B:2"]


def test_mini_event_loop():
    from collections import deque
    class MiniLoop:
        def __init__(self): self.ready = deque()
        def call_soon(self, fn): self.ready.append(fn)
        def run(self):
            out = []
            while self.ready:
                self.ready.popleft()(out)
            return out
    loop = MiniLoop()
    def a_cb(out):
        out.append("a")
        loop.call_soon(lambda o: o.append("a2"))
    loop.call_soon(a_cb)
    loop.call_soon(lambda out: out.append("b"))
    assert loop.run() == ["a", "b", "a2"]


def test_compare_and_swap():
    def cas(cell, expected, new):
        if cell["v"] == expected:
            cell["v"] = new
            return True
        return False
    cell = {"v": 0}
    assert cas(cell, 0, 5) is True and cell["v"] == 5
    assert cas(cell, 0, 9) is False and cell["v"] == 5


# ==========================================================================
# Performance anti-patterns (docs/systems/advanced/)
# ==========================================================================
def test_string_join_matches_concat():
    n = 5000
    s = ""
    for _ in range(n):
        s += "x"
    joined = "".join("x" for _ in range(n))
    assert s == joined == "x" * n


def test_generator_sum_matches_loop():
    total_loop = 0
    for x in range(1000):
        total_loop += x * x
    assert total_loop == sum(x * x for x in range(1000))


# ==========================================================================
# Security (docs/security/) — defensive examples
# ==========================================================================
def test_secret_sharing_reconstructs():
    import random
    random.seed(1)
    mod = 2**31 - 1
    def share(secret, n):
        shares = [random.randrange(mod) for _ in range(n - 1)]
        shares.append((secret - sum(shares)) % mod)
        return shares
    def reconstruct(shares):
        return sum(shares) % mod
    shares = share(42, 3)
    assert reconstruct(shares) == 42


def test_version_vulnerability():
    def pv(v): return tuple(int(p) for p in v.split("."))
    def is_vuln(installed, fixed): return pv(installed) < pv(fixed)
    assert is_vuln("2.25.1", "2.31.0") is True
    assert is_vuln("2.31.0", "2.31.0") is False
    assert is_vuln("2.32.0", "2.31.0") is False


def test_plugin_hash_verify():
    import hashlib
    def phash(code): return hashlib.sha256(code).hexdigest()
    trusted = b"def run(): return 'ok'"
    h = phash(trusted)
    assert phash(trusted) == h
    assert phash(b"def run(): evil()") != h


def test_malware_indicator_scan():
    def find_indicators(data: bytes):
        text = data.decode("latin-1", errors="ignore")
        sus = ["cmd.exe", "powershell", "http://", "CreateRemoteThread"]
        return [s for s in sus if s in text]
    assert find_indicators(b"mentions http:// and cmd.exe") == ["cmd.exe", "http://"]


# ==========================================================================
# Data cleaning & feature engineering (docs/data/intermediate/)
# ==========================================================================
def test_fill_missing_mean():
    def fill(rows, col):
        vals = [r[col] for r in rows if r[col] is not None]
        m = sum(vals) / len(vals)
        for r in rows:
            if r[col] is None:
                r[col] = m
        return rows
    data = [{"age": 30}, {"age": None}, {"age": 50}, {"age": 40}]
    fill(data, "age")
    assert data[1]["age"] == 40.0


def test_one_hot():
    def one_hot(values):
        cats = sorted(set(values))
        return [{c: (1 if v == c else 0) for c in cats} for v in values]
    oh = one_hot(["red", "blue", "red"])
    assert oh[0] == {"blue": 0, "red": 1}
    assert oh[1] == {"blue": 1, "red": 0}


def test_min_max_and_standardize():
    def min_max(vals):
        lo, hi = min(vals), max(vals)
        return [(v - lo) / (hi - lo) for v in vals]
    assert min_max([10, 20, 30]) == [0.0, 0.5, 1.0]
    def standardize(vals):
        m = sum(vals) / len(vals)
        std = (sum((v - m) ** 2 for v in vals) / len(vals)) ** 0.5
        return [(v - m) / std for v in vals]
    assert abs(sum(standardize([2, 4, 6]))) < 1e-9


# ==========================================================================
# ML systems (docs/data/research/)
# ==========================================================================
def test_quantization_roundtrip():
    def quantize(values, bits=8):
        lo, hi = min(values), max(values)
        scale = (hi - lo) / (2 ** bits - 1)
        return [round((v - lo) / scale) for v in values], scale, lo
    def dequantize(q, scale, lo):
        return [x * scale + lo for x in q]
    original = [0.0, 0.25, 0.5, 0.75, 1.0]
    q, scale, lo = quantize(original)
    recovered = dequantize(q, scale, lo)
    assert all(0 <= x <= 255 for x in q)
    assert max(abs(a - b) for a, b in zip(original, recovered)) < 0.01


def test_ml_monitoring_drift():
    def bucketize(values, edges):
        counts = [0] * (len(edges) + 1)
        for v in values:
            for i, e in enumerate(edges):
                if v <= e:
                    counts[i] += 1
                    break
            else:
                counts[-1] += 1
        return [c / len(values) for c in counts]
    def drift(ref, cur, edges):
        p, q = bucketize(ref, edges), bucketize(cur, edges)
        return sum((qi - pi) * math.log(qi / pi)
                   for pi, qi in zip(p, q) if pi > 0 and qi > 0)
    edges = [0, 10, 20]
    ref = [5, 5, 15, 25, 5, 15]
    similar = [5, 6, 15, 24, 4, 16]
    shifted = [25, 26, 27, 28, 29, 30]
    assert drift(ref, shifted, edges) > drift(ref, similar, edges)


def test_inference_graph_dag():
    def run_graph(nodes, inputs):
        results, done, pending = dict(inputs), set(inputs), dict(nodes)
        while pending:
            ran = False
            for name, (func, deps) in list(pending.items()):
                if all(d in done for d in deps):
                    results[name] = func(*[results[d] for d in deps])
                    done.add(name); del pending[name]; ran = True
            if not ran:
                raise ValueError("cycle")
        return results
    graph = {
        "pre": (lambda x: x.strip().lower(), ["raw"]),
        "modelA": (lambda t: len(t), ["pre"]),
        "modelB": (lambda t: t.count("a"), ["pre"]),
        "combine": (lambda a, b: {"len": a, "a_count": b}, ["modelA", "modelB"]),
    }
    out = run_graph(graph, {"raw": "  BANANA  "})
    assert out["combine"] == {"len": 6, "a_count": 3}
