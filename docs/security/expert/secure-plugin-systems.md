---
title: "Secure Plugin Systems"
description: Safely loading and running third-party plugins with isolation and trust boundaries
---

# Secure Plugin Systems <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🔒 Security & DevOps</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="../../web/expert/plugin-based-architectures.md">Plugin-based Architectures</a>, <a href="sandboxing.md">Sandboxing</a></span>
  </div>
</div>

---

## What you'll learn

- [x] The core plugin security problem
- [x] Signature verification (tested)
- [x] Isolation strategies and trust boundaries
- [x] Why in-process Python sandboxing fails
- [x] The safe architecture

[Plugin architectures](../../web/expert/plugin-based-architectures.md) let third parties extend your app — but a plugin is **arbitrary code running in your process**, which is a serious security problem. This page covers how to load plugins *safely*. The signature-verification example is **run-verified**.

---

## The core problem

When your app loads a plugin, that plugin's code runs with **all the privileges your app has** — it can read your files, access your data, make network calls, and use any secret your process holds. A malicious or compromised plugin is a full compromise.

```
   your app (has: files, DB, secrets, network)
        │ loads
        ▼
   plugin code  ──runs with ALL of the above──▶  can do anything your app can
```

So plugin security is about answering two questions: **is this plugin who it claims to be?** (authenticity) and **how do we limit what it can do?** (isolation).

---

## Signature verification (tested)

Before running a plugin, verify it hasn't been tampered with and comes from a trusted source. The mechanism is a cryptographic signature; here's the *integrity* half — verifying a plugin's hash matches an expected value. Runnable:

```python
import hashlib

def plugin_hash(code: bytes) -> str:
    return hashlib.sha256(code).hexdigest()

def verify(code: bytes, expected_hash: str) -> bool:
    """Only load a plugin whose content matches the trusted hash."""
    return plugin_hash(code) == expected_hash

trusted = b"def run(): return 'ok'"
trusted_hash = plugin_hash(trusted)

# Later, before loading:
print("untampered:", verify(trusted, trusted_hash))
tampered = b"def run(): steal_secrets()"
print("tampered:", verify(tampered, trusted_hash))
```

Output:

```text
untampered: True
tampered: False
```

If even one byte of the plugin changes, its hash changes, and `verify` rejects it. Real systems go further — a **digital signature** (the publisher signs the hash with a private key; you verify with their public key) proves *who* published it, not just that it's unchanged. But hash/signature verification only proves authenticity — it does **not** make trusted code *safe to run unrestricted*.

---

## Isolation strategies (trust boundaries)

Since you can't fully trust plugin code, limit what it can reach. From weakest to strongest:

| Strategy | Isolation | Notes |
|---|---|---|
| **In-process, "restricted"** | ❌ Weak | Trying to sandbox within Python — **does not work** (see below) |
| **Separate process** | ✅ Medium | Plugin runs in its own process; communicate via IPC; OS limits it |
| **Container** (Docker) | ✅ Strong | Filesystem/network/resource isolation via the OS |
| **VM / microVM** (Firecracker) | ✅ Strongest | Full isolation; used for truly untrusted code |
| **WASM sandbox** | ✅ Strong | Run plugins compiled to WebAssembly with capability limits |

The pattern: run untrusted plugins **out-of-process** (or in a container/VM/WASM), exposing only a narrow, explicit interface. That interface is the **trust boundary** — the plugin can only do what you deliberately allow through it.

---

## Why in-process Python sandboxing fails

!!! danger "You cannot safely sandbox untrusted Python inside your process"
    It's tempting to think you can restrict a plugin by removing builtins or blocking imports. **This does not work** — Python's introspection is too powerful. There are well-known escapes: reaching dangerous functions through `().__class__.__bases__`, `__subclasses__()`, exception objects, and countless other paths. The old `rexec`/`Bastion` modules were removed precisely because they couldn't be made safe. **Never** run untrusted code in your interpreter and expect restrictions to hold. If code is untrusted, isolate it at the **OS/process/container/VM** level, not within Python. See [Sandboxing](sandboxing.md).

---

## The safe architecture

Putting it together for genuinely untrusted plugins:

1. **Verify** authenticity (signature) before loading anything.
2. **Isolate** execution out-of-process — a separate process, container, or WASM runtime.
3. **Narrow interface** — the plugin communicates only through a defined API/message channel, not shared memory.
4. **Least privilege** — the isolated environment gets only the files, network, and resources it truly needs.
5. **Resource limits** — cap CPU, memory, and time so a plugin can't hang or exhaust the host.

For *trusted* plugins (your own team, vetted partners), in-process loading (as in [Plugin-based Architectures](../../web/expert/plugin-based-architectures.md)) is fine — signature verification plus review is enough. The heavy isolation is for **untrusted** third-party code.

!!! tip "Match isolation to trust"
    First-party/vetted plugins → in-process is fine (verify + review). Untrusted third-party code → out-of-process/container/VM/WASM, always. Don't over-engineer trusted plugins, and never under-protect untrusted ones.

---

## Practice exercises

1. Extend the verifier to check a real signature (public-key verify a signed hash) rather than a bare hash.
2. Sketch running a plugin in a subprocess that communicates over stdin/stdout with a JSON protocol.
3. Research one Python sandbox-escape technique and explain why in-process restriction fails.
4. Design the trust boundary (allowed operations) for a plugin that should only transform text.
5. Decide the isolation level for: (a) your own team's plugin, (b) a plugin from the public internet — and justify each.
