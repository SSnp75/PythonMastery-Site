---
title: Quantum Computing
description: Qiskit, quantum circuits, simulation and quantum algorithms
---

# Quantum Computing <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>🔬 Research Track · Level 7</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Open-ended</span>
  </div>
</div>

---

## Core ideas

- A **qubit** is a unit vector in a 2D complex space: `α|0⟩ + β|1⟩` with `|α|² + |β|² = 1`.
- **Measurement** collapses it to `0` or `1` with probabilities `|α|²` and `|β|²`.
- **Gates** are unitary matrices (Hadamard, Pauli-X, CNOT) that rotate the state.
- **Entanglement** correlates qubits so measuring one determines the other.

---

## A pure-Python single-qubit simulator

No libraries needed — a qubit is just two complex amplitudes, and a gate is a 2×2 matrix:

```python
import cmath

# |0> state
state = [1 + 0j, 0 + 0j]

# Hadamard gate puts |0> into an equal superposition
h = 1 / cmath.sqrt(2)
H = [[h, h], [h, -h]]

def apply(gate, s):
    return [gate[0][0] * s[0] + gate[0][1] * s[1],
            gate[1][0] * s[0] + gate[1][1] * s[1]]

state = apply(H, state)
p0 = abs(state[0]) ** 2
p1 = abs(state[1]) ** 2
print(round(p0, 3), round(p1, 3))   # 0.5 0.5  (equal superposition)
```

This is exactly what a quantum SDK does under the hood, scaled to `2ⁿ` amplitudes for `n`
qubits.

---

## Qiskit basics

With a real framework you build circuits declaratively and run them on a simulator or
hardware:

```python
# pip install qiskit qiskit-aer
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

qc = QuantumCircuit(2, 2)
qc.h(0)              # Hadamard — superposition on qubit 0
qc.cx(0, 1)          # CNOT — entangle qubit 1 with qubit 0
qc.measure([0, 1], [0, 1])

sim = AerSimulator()
result = sim.run(qc, shots=1000).result()
print(result.get_counts())   # {'00': ~500, '11': ~500} — a Bell state
```

The `~50/50` split across `00` and `11` (never `01` or `10`) is the signature of
entanglement.

---

## Where to go next

*Gates, algorithms, error correction, and other SDKs to explore.*

- **Gates:** Pauli-X/Y/Z, phase, Toffoli
- **Algorithms:** Grover's search, Deutsch–Jozsa, Shor's factoring
- **Variational:** VQE, QAOA for optimization
- **Error correction:** surface codes
- **Other SDKs:** Cirq (Google), PennyLane (quantum ML)

---

## Practice exercises

1. Add a Pauli-X gate (`[[0,1],[1,0]]`) to the pure-Python simulator and confirm it flips `|0⟩` to `|1⟩`.
2. Apply Hadamard twice and verify the state returns to `|0⟩`.
3. Compute the probabilities after applying `H` to the `|1⟩` state.
4. Extend the simulator to two qubits using a length-4 amplitude vector.
