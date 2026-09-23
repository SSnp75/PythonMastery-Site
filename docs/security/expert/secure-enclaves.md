---
title: "Secure Enclaves"
description: Trusted execution environments for protecting code and data in use
---

# Secure Enclaves <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🔒 Security & DevOps</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="cryptography.md">Cryptography</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What a secure enclave / TEE is
- [x] The "data in use" protection gap it fills
- [x] SGX, SEV, and confidential computing
- [x] How Python fits
- [x] Threat model and limits

A **secure enclave** (or **Trusted Execution Environment**, TEE) is a hardware-protected region of a CPU where code and data are shielded — even from the operating system, hypervisor, and cloud provider. It's how you run sensitive computation on infrastructure you don't fully trust.

!!! note "This is a hardware/infrastructure topic"
    Enclaves are a CPU/platform feature accessed through specialized SDKs, not a Python library you script directly. This page is conceptual — there's no meaningful runnable Python snippet. It orients you to the technology and how Python relates to it.

---

## The "data in use" gap

Encryption traditionally protects data in two states, leaving a gap:

```
   data AT REST   → encrypted on disk        ✅ (full-disk / file encryption)
   data IN TRANSIT → encrypted on the wire   ✅ (TLS)
   data IN USE     → decrypted in memory     ❌ ← the gap enclaves fill
```

To *compute* on data, you normally decrypt it into RAM — where the OS, a compromised admin, or a malicious cloud host could read it. Secure enclaves close this gap: data stays protected **even while being processed**, inside a hardware-isolated region.

---

## The technologies

- **Intel SGX** (Software Guard Extensions) — creates encrypted memory "enclaves"; even the OS kernel can't read enclave memory.
- **AMD SEV** (Secure Encrypted Virtualization) — encrypts a whole VM's memory, protecting it from the hypervisor/host.
- **ARM TrustZone** — a "secure world" on ARM chips (common in mobile/embedded).
- **AWS Nitro Enclaves, Azure Confidential Computing, Google Confidential VMs** — cloud offerings built on these.

Collectively this is **confidential computing** — a growing field for running sensitive workloads on shared/cloud infrastructure.

---

## Attestation: proving what's running

A key concept is **remote attestation** — the enclave can cryptographically *prove* to a remote party exactly what code is running inside it and that it's genuinely protected by real hardware. Before sending secret data to an enclave, you verify its attestation. This is what lets you trust computation on someone else's machine: not "trust the operator," but "trust the hardware's proof of what's executing."

---

## How Python fits

Python isn't the natural language for enclave code (which is often C/C++ for the small trusted core), but it appears at the edges:

- **Orchestration** — Python code outside the enclave sets up, attests, and communicates with it.
- **Confidential VMs** — with AMD SEV / cloud confidential VMs, you can run *ordinary* Python inside a memory-encrypted VM with little change — the protection is at the VM level.
- **Frameworks** — projects like Gramine let existing applications (including Python) run inside SGX enclaves with minimal modification.

So the common pattern for Python + enclaves today is a **confidential VM**: run your normal Python workload inside a hardware-encrypted VM, gaining "data in use" protection without rewriting for a tiny C enclave.

---

## Threat model and limits

!!! warning "Enclaves are not magic"
    Secure enclaves defend against a specific threat: a compromised OS/hypervisor/host reading your data *in use*. They do **not** fix bugs in *your* code, protect against side-channel attacks (several have been demonstrated against SGX), or remove the need for other security practices. They also add complexity and performance overhead. Use them when your threat model genuinely includes an untrusted host — and combine with, not instead of, the rest of your security.

---

## Practice exercises

1. Explain the three data states (rest, transit, in use) and which each common protection covers.
2. Describe remote attestation and why it lets you trust computation on an untrusted machine.
3. Compare Intel SGX (enclave) with AMD SEV (encrypted VM) in terms of what runs protected.
4. Explain why a "confidential VM" is often the easier path for running Python confidentially.
5. Give a concrete workload where the complexity of enclaves is justified, and one where it isn't.
