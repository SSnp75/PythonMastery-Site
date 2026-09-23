---
title: "Homomorphic Encryption"
description: Compute on encrypted data without ever decrypting it
---

# Homomorphic Encryption <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🔒 Security & DevOps</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="cryptography.md">Cryptography</a>, modular arithmetic</span>
  </div>
</div>

---

## What you'll learn

- [x] What homomorphic encryption enables
- [x] The homomorphic property (illustrated, tested)
- [x] Partial vs fully homomorphic
- [x] Performance reality
- [x] Libraries and use cases

**Homomorphic Encryption (HE)** lets you compute on *encrypted* data and get an encrypted result that, when decrypted, matches the computation on the plaintext. A cloud server can process your data **without ever seeing it**. This page is **educational**; the illustration of the homomorphic *property* is run-verified, but real HE requires specialized libraries.

---

## The idea

```
   plaintext ──encrypt──▶ ciphertext ──compute on ciphertext──▶ encrypted result
                                                                      │ decrypt
                                                                      ▼
                                          result == computation on the plaintext
```

Normally, to compute on data you must decrypt it — exposing it to whoever's doing the computing. HE breaks that: the server operates on ciphertext and never has the key. You send encrypted data, it computes, sends back an encrypted answer only *you* can decrypt.

---

## The homomorphic property (illustrated, tested)

The core idea is that an operation on ciphertexts corresponds to an operation on plaintexts. A *toy* illustration using multiplication as the "encryption" (NOT secure — just to show the property):

```python
# TOY illustration of the homomorphic PROPERTY (not real, not secure).
# "Encrypt" by multiplying by a secret key; multiplication is homomorphic here.
KEY = 7

def enc(x):
    return x * KEY            # toy "ciphertext"

def dec(c):
    return c // KEY

a, b = 3, 5
ca, cb = enc(a), enc(b)

# multiply ciphertexts, then decrypt — with a key correction for the toy scheme
product_cipher = ca * cb
decrypted = product_cipher // (KEY * KEY)      # undo both key factors
print("computed on ciphertext, decrypted:", decrypted)
print("plaintext product:", a * b)
```

Output:

```text
computed on ciphertext, decrypted: 15
plaintext product: 15
```

Operating on the "ciphertexts" and decrypting gave `15` = `3 × 5` — **we computed the product without using the plaintexts directly in the multiplication**. That's the homomorphic *property* in essence.

!!! danger "This toy scheme is NOT encryption"
    Multiplying by a constant is trivially breakable — it's shown *only* to illustrate what "an operation on ciphertexts maps to an operation on plaintexts" means. **Real HE** (like the BFV/CKKS schemes) uses lattice-based cryptography with noise, and is genuinely secure. Never use anything like the toy above to protect data.

---

## Partial vs fully homomorphic

HE schemes differ by *which* operations they support:

- **Partially Homomorphic (PHE)** — supports *one* operation unlimited times. E.g. RSA is multiplicatively homomorphic; Paillier is additively homomorphic (great for summing encrypted votes/values).
- **Somewhat Homomorphic (SHE)** — supports both add and multiply, but only a limited number (noise grows with each operation).
- **Fully Homomorphic (FHE)** — supports *arbitrary* computation via **bootstrapping** (a noise-reduction step). The holy grail, achieved by Gentry in 2009; still expensive but improving.

The breakthrough that made FHE possible was **bootstrapping** — periodically "refreshing" a ciphertext to reduce accumulated noise, allowing unlimited operations.

---

## The performance reality

!!! warning "HE is slow — that's the catch"
    Homomorphic encryption is orders of magnitude slower and larger than plaintext computation — a single operation can be thousands of times slower, and ciphertexts are much bigger than plaintexts. FHE especially remains impractical for general heavy computation today. It's used where **privacy justifies the cost**, not as a default. Performance is improving steadily but it's not "encrypt everything and compute freely" yet.

---

## Libraries and use cases

Python libraries (documented, not installed here): **Pyfhel**, **TenSEAL** (HE for tensors/ML), **Microsoft SEAL** bindings, **OpenFHE**. They implement the real lattice-based schemes.

Where HE is worth the cost:
- **Private cloud computation** — process sensitive data (medical, financial) on untrusted infrastructure without exposing it.
- **Privacy-preserving ML inference** — run a model on encrypted inputs (TenSEAL).
- **Encrypted database queries** — search/aggregate without the server seeing data.
- **Secure aggregation** — sum encrypted values (additive PHE like Paillier is practical here).

It overlaps with [SMPC](smpc.md) — both let you compute without exposing data, via different cryptographic routes.

---

## Practice exercises

1. Explain in your own words the difference between partial, somewhat, and fully homomorphic encryption.
2. Describe why the toy multiply-by-key scheme is insecure despite showing the homomorphic property.
3. Explain what "bootstrapping" solves and why it enabled fully homomorphic encryption.
4. Give a concrete scenario where HE's slowness is an acceptable price.
5. Compare HE and SMPC — how does each let parties compute without revealing data?
