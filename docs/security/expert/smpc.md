---
title: "SMPC"
description: Secure multiparty computation — compute on data without revealing it
---

# SMPC — Secure Multiparty Computation <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🔒 Security & DevOps</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="cryptography.md">Cryptography</a>, modular arithmetic</span>
  </div>
</div>

---

## What you'll learn

- [x] What SMPC enables
- [x] Additive secret sharing (tested)
- [x] Computing on shares without revealing them (tested)
- [x] Real protocols and libraries
- [x] Where SMPC is used

**Secure Multiparty Computation (SMPC)** lets several parties jointly compute a result over their combined data **without any party revealing its private input**. The classic example: a group of people compute their average salary without anyone learning anyone else's salary. The secret-sharing core here is **run-verified**.

---

## The idea

```
   Alice's secret ─┐
   Bob's secret   ─┼──▶ joint computation ──▶ result
   Carol's secret ─┘        (nobody sees
                             others' inputs)
```

Each party keeps its input private, yet together they get the correct answer. This sounds paradoxical, but cryptography makes it work — one foundational technique is **secret sharing**.

---

## Additive secret sharing (tested)

Split a secret into `n` **shares** that individually look random, but sum back to the secret (modulo a prime). No single share reveals anything. Runnable:

```python
import random
random.seed(1)

def share(secret, n, modulus=2**31 - 1):
    """Split `secret` into n additive shares; their sum mod p is the secret."""
    shares = [random.randrange(modulus) for _ in range(n - 1)]
    last = (secret - sum(shares)) % modulus
    shares.append(last)
    return shares, modulus

def reconstruct(shares, modulus):
    return sum(shares) % modulus

secret = 42
shares, mod = share(secret, n=3)
print("reconstructed:", reconstruct(shares, mod))
```

Output:

```text
reconstructed: 42
```

The secret 42 is split into 3 shares. Each share is a random-looking number — hold just one (or even two) and you learn *nothing* about the secret. Only all three together reconstruct it. You'd give each party one share.

---

## Computing on shares (the magic, tested)

Here's what makes SMPC powerful: you can **add two shared secrets without reconstructing either** — just add the shares position-wise, and the result is a valid sharing of the sum:

```python
shares_a, mod = share(42, 3)
shares_b, _   = share(58, 3)

# each party adds their two shares locally — no secrets revealed
sum_shares = [(a + b) % mod for a, b in zip(shares_a, shares_b)]

print("sum reconstructed:", reconstruct(sum_shares, mod))
```

Output:

```text
sum reconstructed: 100
```

`42 + 58 = 100` — computed correctly, yet no party ever saw the other's number. Each party only combined *their own* shares locally. This is the essence of SMPC: operations on shares mirror operations on the secrets. Addition is easy (shown here); multiplication is much harder and needs more elaborate protocols.

---

## Real protocols and libraries

Our example shows additive sharing (great for sums/averages). Full SMPC uses richer schemes:

- **Shamir's Secret Sharing** — polynomial-based, allows *threshold* reconstruction (any k of n shares).
- **Garbled circuits** (Yao) — for secure two-party computation of arbitrary functions.
- **BGW / SPDZ protocols** — support multiplication and general computation.

Python libraries (documented, not installed here): **PySyft**, **MP-SPDZ**, **CrypTen** (privacy-preserving ML). These handle the hard parts (secure multiplication, malicious-party resistance) that our simple additive scheme doesn't.

!!! warning "Don't roll your own for production"
    The additive sharing above is correct for *learning* and for simple additive cases, but real SMPC must resist malicious parties, handle multiplication, and manage communication rounds securely. Cryptographic protocols have subtle failure modes — use audited libraries (and expert review) for anything real. This page is educational.

---

## Where SMPC is used

- **Privacy-preserving analytics** — compute aggregate statistics across organizations without sharing raw data (e.g. hospitals studying outcomes without exposing patient records).
- **Private machine learning** — train/infer on combined datasets while keeping each party's data private (CrypTen, federated learning overlaps).
- **Secure auctions/voting** — determine a winner/tally without revealing individual bids/votes.
- **Key management** — threshold schemes where k of n parties must cooperate to use a key.

It's closely related to [Homomorphic Encryption](homomorphic-encryption.md) (compute on encrypted data) — different techniques, overlapping goal of computing without exposing data.

---

## Practice exercises

1. Extend `share`/`reconstruct` to average N parties' values (share each, sum shares, divide by N).
2. Verify that any single share (or any n-1 shares) is uniformly random and reveals nothing about the secret.
3. Explain why *addition* on shares is easy but *multiplication* needs a special protocol.
4. Research Shamir's Secret Sharing and explain how threshold (k-of-n) reconstruction differs from additive.
5. Describe a real scenario (analytics or ML) where SMPC lets parties cooperate without trusting each other with raw data.
