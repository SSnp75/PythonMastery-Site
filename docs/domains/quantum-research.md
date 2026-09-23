---
title: "Python for Quantum Research"
description: Qubits, quantum circuits and algorithms with Python and Qiskit
---

# Python for Quantum Research <span class="pm-badge pm-badge-research">Domain</span>

<div class="pm-topic-header">
  <strong>🌍 Domain Applications</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 weeks</span>
    <span>📚 Prereqs: <a href="../scientific/index.md">Scientific Computing</a>, linear algebra</span>
  </div>
</div>

---

## What you'll learn

- [x] What a qubit is (and how it differs from a bit)
- [x] Superposition and entanglement, intuitively
- [x] Quantum gates and circuits
- [x] Simulating a qubit with plain math (tested)
- [x] The Qiskit ecosystem

Quantum computing is an emerging field where Python is the primary language for research, via frameworks like Qiskit and Cirq. This page builds intuition and shows a **run-verified** classical simulation of a single qubit; real quantum frameworks follow documented APIs.

---

## Bits vs qubits

A classical **bit** is 0 or 1. A **qubit** can be in a *superposition* — a combination of both at once, described by two complex amplitudes:

```
   |ψ⟩ = α|0⟩ + β|1⟩      where |α|² + |β|² = 1
```

`|α|²` is the probability of measuring 0, `|β|²` the probability of measuring 1. Measuring **collapses** the superposition to a definite 0 or 1. This is what gives quantum computers their potential: `n` qubits represent `2ⁿ` amplitudes simultaneously.

---

## Simulating one qubit (tested)

A single qubit's state is just two numbers, and gates are small matrix multiplications — pure math you can do with the standard library. Here's the **Hadamard gate**, which puts `|0⟩` into an equal superposition. Runnable:

```python
import cmath

# State |0> = [1, 0], |1> = [0, 1]. A gate is a 2x2 matrix.
def apply_gate(gate, state):
    return [
        gate[0][0]*state[0] + gate[0][1]*state[1],
        gate[1][0]*state[0] + gate[1][1]*state[1],
    ]

h = 1 / cmath.sqrt(2)
HADAMARD = [[h, h], [h, -h]]

state0 = [1, 0]                      # start in |0>
after = apply_gate(HADAMARD, state0)
p0 = abs(after[0])**2
p1 = abs(after[1])**2
print(f"P(0) = {p0:.2f}, P(1) = {p1:.2f}")
```

Output:

```text
P(0) = 0.50, P(1) = 0.50
```

Applying Hadamard to `|0⟩` gives a 50/50 superposition — measure it and you get 0 or 1 with equal probability. This *is* quantum computing's core mechanic, done as a 2×2 matrix times a vector. Real simulators do exactly this at scale (which is why simulating many qubits classically is exponentially expensive — the state vector doubles per qubit).

---

## Superposition and entanglement

- **Superposition** (above) — a qubit being a blend of 0 and 1 until measured.
- **Entanglement** — two qubits linked so that measuring one instantly determines the other, regardless of distance. This correlation, with no classical equivalent, is central to quantum algorithms. The "Bell state" is the simplest entangled pair.

These two phenomena — superposition for parallelism, entanglement for correlation — are the resources quantum algorithms exploit.

---

## Gates, circuits, and Qiskit

Quantum programs are **circuits**: sequences of gates applied to qubits, then measurement. **Qiskit** (IBM) is the leading Python framework:

```python
from qiskit import QuantumCircuit    # pip install qiskit

qc = QuantumCircuit(2, 2)            # 2 qubits, 2 classical bits
qc.h(0)                             # Hadamard on qubit 0 -> superposition
qc.cx(0, 1)                         # CNOT -> entangle qubits 0 and 1 (Bell state)
qc.measure([0, 1], [0, 1])
# running this yields ~50% '00' and ~50% '11' — never '01' or '10' (entanglement)
```

!!! note "Qiskit snippet follows documented API"
    Qiskit isn't installed here, so this isn't run-verified (the single-qubit simulation above is). Qiskit can run circuits on simulators *or* real quantum hardware over the cloud. The Bell-state result — only `00` or `11`, never mixed — is the signature of entanglement.

---

## Famous quantum algorithms

- **Grover's search** — find an item in an unsorted database in ~√N steps (vs N classically).
- **Shor's algorithm** — factor large numbers efficiently; famously threatens RSA encryption (see the Security section's Cryptography).
- **Quantum simulation** — model quantum systems (chemistry, materials) — arguably the most practical near-term use.

These need many reliable qubits; today's hardware is "noisy intermediate-scale quantum" (NISQ) — limited and error-prone. The field is early.

---

## The ecosystem

| Need | Tool |
|---|---|
| Circuits + hardware | Qiskit (IBM), Cirq (Google) |
| Simulation | Qiskit Aer, NumPy |
| ML + quantum | PennyLane |
| Math backbone | NumPy (linear algebra) |

---

## Practice exercises

1. Add the **X gate** `[[0,1],[1,0]]` (quantum NOT) and confirm it flips `|0⟩` to `|1⟩`.
2. Apply Hadamard twice to `|0⟩` and show it returns to `|0⟩` (H is its own inverse).
3. Verify `|α|² + |β|²` stays 1 after applying a gate (states stay normalized).
4. Explain, in plain words, why simulating n qubits classically needs 2ⁿ numbers.
5. Describe what makes an entangled Bell state produce only `00`/`11` and never `01`/`10`.
