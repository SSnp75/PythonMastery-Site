---
title: "Networking Automation"
description: Automate network devices with SSH, device APIs and idempotent configuration
---

# Networking Automation <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🔧 Embedded & Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisites: <a href="../../automation/scripting/">Automation & Scripting</a>, <a href="../../web/proficient/apis-http/">APIs & HTTP</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Automate device config over SSH
- [x] Use vendor-neutral libraries (Netmiko, NAPALM)
- [x] Compute an idempotent config diff
- [x] Understand configuration management for networks
- [x] Automate safely across many devices

---

## Why automate the network

Configuring routers, switches, and firewalls by hand — logging into each one and typing commands — doesn't scale and invites human error. **Network automation (NetOps)** applies software practices to network devices: push config from scripts, verify state programmatically, and treat the network config as version-controlled code. Python dominates this space thanks to libraries like Netmiko, NAPALM, and Nornir.

```
   ┌──────────────┐   SSH / API   ┌────────┐ ┌────────┐ ┌────────┐
   │ Python script │ ────────────▶ │ router │ │ switch │ │firewall│
   │ (source of    │   push config │  r1    │ │  sw1   │ │  fw1   │
   │  truth)       │   read state  └────────┘ └────────┘ └────────┘
   └──────────────┘
```

---

## SSH to a device with Netmiko

Most network gear is driven over SSH. **Netmiko** wraps the messy details (vendor prompts, paging, timing) into a clean API:

```python
from netmiko import ConnectHandler   # pip install netmiko

device = {
    "device_type": "cisco_ios",
    "host": "10.0.0.1",
    "username": "admin",
    "password": "secret",     # in practice: from a secrets manager, not code
}

with ConnectHandler(**device) as conn:
    output = conn.send_command("show ip interface brief")
    print(output)

    # push configuration lines
    conn.send_config_set(["ntp server 2.2.2.2"])
```

!!! note "Netmiko needs the package and real devices"
    This uses `netmiko` against actual network hardware, so it isn't run-verified here. The **config-diff logic below is pure stdlib and tested.** Note the password is shown inline only for clarity — real automation pulls credentials from environment variables or a secrets manager (see the Secrets Management topic), never hard-coded.

**NAPALM** goes further with a *vendor-neutral* API: the same Python calls (`get_facts`, `load_merge_candidate`, `commit_config`) work across Cisco, Juniper, Arista, and more — so one script manages a mixed fleet.

---

## Idempotency: the core discipline

The single most important idea in configuration automation is **idempotency** — applying the same desired state repeatedly produces the same result, making no changes after the first. You don't blindly re-push config; you compute the *difference* between what's running and what you want, and apply only that. Fully runnable:

```python
def config_diff(running: list[str], desired: list[str]) -> dict[str, list[str]]:
    """Compare running vs desired config; return what to add and remove."""
    run_set, des_set = set(running), set(desired)
    return {
        "add":    sorted(des_set - run_set),   # in desired but not running
        "remove": sorted(run_set - des_set),   # in running but not desired
    }
```

```python
running = ["hostname r1", "ip route 0.0.0.0/0 10.0.0.1", "ntp server 1.1.1.1"]
desired = ["hostname r1", "ip route 0.0.0.0/0 10.0.0.1", "ntp server 2.2.2.2"]

diff = config_diff(running, desired)
print("to add:   ", diff["add"])
print("to remove:", diff["remove"])
```

Output:

```text
to add:    ['ntp server 2.2.2.2']
to remove: ['ntp server 1.1.1.1']
```

Only the NTP server changed, so the diff proposes exactly one addition and one removal — the hostname and route are left untouched. And it's idempotent: run `config_diff(desired, desired)` and you get `{"add": [], "remove": []}` — nothing to do, because the device already matches. This "converge to desired state" model is how tools like Ansible and Terraform work: describe the target, let the tool figure out the minimal change.

!!! tip "Declare the desired state, don't script the steps"
    Imperative automation ("run these 5 commands") breaks if the device is already in a partial state. Declarative automation ("here is the config I want") plus a diff is safe to run repeatedly — the foundation of reliable config management.

---

## Configuration management at scale

For many devices, you graduate from scripts to frameworks:

- **Ansible** — agentless, YAML playbooks, huge library of network modules. The common starting point.
- **Nornir** — a pure-Python automation framework; you write Python (not YAML), with built-in inventory and parallelism across devices.
- **NAPALM** — the vendor-neutral driver layer many of these build on.

A typical workflow: keep the desired config in **git** (version-controlled source of truth), run it through CI, and have the tool converge each device to match — with a diff shown for approval before anything is applied.

---

## Automating safely

Network changes can take down connectivity — including your own path to the device. Guardrails:

- **Dry-run first.** Compute and review the diff (like above) before applying. Most tools have a `--check`/dry-run mode.
- **Config backups.** Snapshot the running config before every change so you can roll back.
- **Commit-confirm.** Some platforms let a change auto-revert unless you confirm within N minutes — a lifesaver if a change locks you out.
- **Stage rollouts.** Apply to one device, verify, then proceed — don't push to the whole fleet at once (echoes the rolling-update idea from [Hot-swappable Components](../web/expert/hot-swappable-components.md)).
- **Protect credentials.** Device passwords and API keys come from a secrets store, never the script or git.

!!! warning "You can cut off your own access"
    A bad ACL or interface change can sever the SSH session you're managing the device through. Always have out-of-band access (console/management port) or commit-confirm enabled before pushing risky changes to remote gear.

---

## Practice exercises

1. Extend `config_diff` to also report an `"unchanged"` list, and confirm it's the intersection of the two sets.
2. Make the diff order-aware for commands where order matters (some ACLs), instead of using sets.
3. Write a function that takes a diff and produces the ordered command list to apply (removals first, then additions) — and explain why that order.
4. Read desired config from a file and running config from another, and print the diff — a mini config-drift detector.
5. Explain idempotency to a colleague using the NTP-server example, and why it makes re-running safe.
