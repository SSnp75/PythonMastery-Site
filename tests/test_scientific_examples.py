"""Tests for runnable examples in the Scientific Computing & Domains docs.

Mirrors the site examples so CI fails if one breaks. Pure standard library.
"""
from __future__ import annotations
import math


# --------------------------------------------------------------------------
# Numerical optimization (docs/scientific/numerical-optimization.md)
# --------------------------------------------------------------------------
def bisect(f, lo, hi, tol=1e-9):
    assert f(lo) * f(hi) < 0
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def newton(f, df, x0, iters=20):
    x = x0
    for _ in range(iters):
        x = x - f(x) / df(x)
    return x


def gradient_descent(grad, x0, lr=0.1, iters=100):
    x = x0
    for _ in range(iters):
        x = x - lr * grad(x)
    return x


def test_bisection_sqrt2():
    assert abs(bisect(lambda x: x * x - 2, 0, 2) - math.sqrt(2)) < 1e-6


def test_newton_sqrt2():
    r = newton(lambda x: x * x - 2, lambda x: 2 * x, 1.0)
    assert abs(r - math.sqrt(2)) < 1e-9


def test_gradient_descent_minimum():
    assert round(gradient_descent(lambda x: 2 * (x - 3), 0.0), 4) == 3.0


# --------------------------------------------------------------------------
# Computational physics (docs/scientific/computational-physics.md)
# --------------------------------------------------------------------------
def integrate(f, a, b, n=1000):
    h = (b - a) / n
    total = (f(a) + f(b)) / 2
    for i in range(1, n):
        total += f(a + i * h)
    return total * h


def euler(dydt, y0, t0, t1, steps):
    dt = (t1 - t0) / steps
    y, t = y0, t0
    for _ in range(steps):
        y += dydt(t, y) * dt
        t += dt
    return y


def test_trapezoidal_integration():
    assert abs(integrate(lambda x: x * x, 0, 1) - 1 / 3) < 1e-4
    assert abs(integrate(math.sin, 0, math.pi) - 2.0) < 1e-4


def test_euler_decay():
    approx = euler(lambda t, y: -y, 1.0, 0, 1, 1000)
    assert abs(approx - math.exp(-1)) < 0.01


def test_monte_carlo_pi():
    import random
    random.seed(42)
    inside = 0
    n = 100_000
    for _ in range(n):
        x, y = random.random(), random.random()
        if x * x + y * y <= 1:
            inside += 1
    assert abs(4 * inside / n - math.pi) < 0.05


# --------------------------------------------------------------------------
# BLAS naive matmul (docs/scientific/blas-lapack.md)
# --------------------------------------------------------------------------
def matmul(A, B):
    n, m, p = len(A), len(B), len(B[0])
    result = [[0] * p for _ in range(n)]
    for i in range(n):
        for k in range(m):
            aik = A[i][k]
            for j in range(p):
                result[i][j] += aik * B[k][j]
    return result


def test_matmul():
    assert matmul([[1, 2], [3, 4]], [[5, 6], [7, 8]]) == [[19, 22], [43, 50]]


# --------------------------------------------------------------------------
# Sparse vector (docs/scientific/sparse-tensors.md)
# --------------------------------------------------------------------------
class SparseVector:
    def __init__(self, data: dict):
        self.data = {i: v for i, v in data.items() if v != 0}

    def dot(self, other: "SparseVector") -> float:
        common = self.data.keys() & other.data.keys()
        return sum(self.data[k] * other.data[k] for k in common)


def test_sparse_vector():
    a = SparseVector({0: 1, 5: 2, 999: 3})
    b = SparseVector({5: 4, 999: 1, 7: 9})
    assert a.dot(b) == 11
    assert len(a.data) == 3


# --------------------------------------------------------------------------
# Custom autograd (docs/scientific/custom-autograd.md)
# --------------------------------------------------------------------------
class Value:
    def __init__(self, data, _children=()):
        self.data = data
        self.grad = 0.0
        self._backward = lambda: None
        self._prev = set(_children)

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other))
        def _backward():
            self.grad += out.grad
            other.grad += out.grad
        out._backward = _backward
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other))
        def _backward():
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad
        out._backward = _backward
        return out

    def backward(self):
        topo, visited = [], set()
        def build(v):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build(child)
                topo.append(v)
        build(self)
        self.grad = 1.0
        for v in reversed(topo):
            v._backward()


def test_autograd():
    x = Value(3.0)
    y = Value(4.0)
    f = x * y + x
    f.backward()
    assert f.data == 15.0
    assert x.grad == 5.0    # df/dx = y + 1
    assert y.grad == 3.0    # df/dy = x


# --------------------------------------------------------------------------
# Computational biology: edit distance (docs/scientific/computational-biology.md)
# --------------------------------------------------------------------------
def edit_distance(a: str, b: str) -> int:
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return dp[m][n]


def test_edit_distance():
    assert edit_distance("GATTACA", "GATGCA") == 2
    assert edit_distance("AAAA", "AAAA") == 0


# --------------------------------------------------------------------------
# Domains: bioinformatics sequence ops (docs/domains/bioinformatics.md)
# --------------------------------------------------------------------------
def complement(dna: str) -> str:
    pairs = {"A": "T", "T": "A", "C": "G", "G": "C"}
    return "".join(pairs[b] for b in dna)


def test_dna_complement():
    assert complement("GATTACA") == "CTAATGT"
    assert complement("GATTACA")[::-1] == "TGTAATC"


# --------------------------------------------------------------------------
# Domains: GIS haversine (docs/domains/gis.md)
# --------------------------------------------------------------------------
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def test_haversine_london_paris():
    d = haversine_km(51.5074, -0.1278, 48.8566, 2.3522)
    assert 340 < d < 350    # ~343.6 km


# --------------------------------------------------------------------------
# Domains: quantum single-qubit Hadamard (docs/domains/quantum-research.md)
# --------------------------------------------------------------------------
def test_hadamard_superposition():
    import cmath
    def apply_gate(gate, state):
        return [gate[0][0] * state[0] + gate[0][1] * state[1],
                gate[1][0] * state[0] + gate[1][1] * state[1]]
    h = 1 / cmath.sqrt(2)
    after = apply_gate([[h, h], [h, -h]], [1, 0])
    assert abs(abs(after[0]) ** 2 - 0.5) < 1e-9
    assert abs(abs(after[1]) ** 2 - 0.5) < 1e-9
