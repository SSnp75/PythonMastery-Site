---
title: "Plugin-based Architectures"
description: Build extensible systems where features plug in without touching the core
---

# Plugin-based Architectures <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🌐 Web & APIs Track · Level 6</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="../competent/packaging/">Python Packaging</a>, <a href="../../core/advanced/import-system/">Import System</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Build a plugin registry with decorators
- [x] Define stable extension points (contracts)
- [x] Discover plugins dynamically — including from separate packages
- [x] Version and isolate plugins safely
- [x] Know when a plugin system is worth it

---

## The idea

A plugin architecture lets you add features **without modifying the core**. The core defines *extension points* (what a plugin must provide) and a *registry* (how plugins announce themselves). New capabilities arrive as self-contained plugins that snap in.

You've used this everywhere: pytest fixtures/plugins, Flask extensions, VS Code extensions, Django apps. The core stays small and stable; the ecosystem grows around it.

```
        ┌──────────── CORE ────────────┐
        │  extension point (contract)   │
        │  plugin registry              │
        └───────────────┬───────────────┘
             ┌───────────┼───────────┐
        [plugin A]   [plugin B]   [plugin C]   ← added without touching core
```

---

## A registry with decorators

The simplest, most Pythonic plugin system: a dict registry populated by a decorator. Fully runnable.

```python
registry: dict[str, type] = {}

def register(name: str):
    """Decorator that adds a class to the registry under `name`."""
    def deco(cls):
        registry[name] = cls
        return cls
    return deco
```

### The extension point (contract)

Every plugin must satisfy this interface — that's the *contract* the core relies on:

```python
class Exporter:
    def export(self, data: dict) -> str: ...
```

### Plugins

Each plugin is a class that implements the contract and registers itself:

```python
import json

@register("json")
class JsonExporter(Exporter):
    def export(self, data: dict) -> str:
        return json.dumps(data)

@register("csv")
class CsvExporter(Exporter):
    def export(self, data: dict) -> str:
        return ";".join(f"{k}={v}" for k, v in data.items())
```

### The core uses plugins by name

```python
def get_exporter(name: str) -> Exporter:
    if name not in registry:
        raise KeyError(f"no plugin named {name!r}; available: {sorted(registry)}")
    return registry[name]()
```

Running it:

```python
data = {"a": 1, "b": 2}
print("available:", sorted(registry))
print("json ->", get_exporter("json").export(data))
print("csv  ->", get_exporter("csv").export(data))
get_exporter("xml")   # not registered
```

Output:

```text
available: ['csv', 'json']
json -> {"a": 1, "b": 2}
csv  -> a=1;b=2
Traceback (most recent call last):
  ...
KeyError: "no plugin named 'xml'; available: ['csv', 'json']"
```

**The payoff:** adding an `XmlExporter` means writing one new `@register("xml")` class — in this file *or any other module that gets imported*. `get_exporter` and the rest of the core never change. The error message even lists what's available, which is exactly the kind of helpful failure a plugin system should give.

---

## Discovering plugins from separate packages

A registry only knows about plugins whose module has been **imported**. For plugins shipped as their own installable packages, Python's standard mechanism is **entry points** declared in packaging metadata.

A plugin package declares in its `pyproject.toml`:

```toml
[project.entry-points."myapp.exporters"]
yaml = "myapp_yaml_plugin:YamlExporter"
```

The host application discovers all installed plugins at runtime:

```python
from importlib.metadata import entry_points

def load_plugins(group: str) -> dict[str, type]:
    found = {}
    for ep in entry_points(group=group):
        found[ep.name] = ep.load()    # imports and returns the class
    return found

# plugins = load_plugins("myapp.exporters")
# -> {'yaml': <class 'myapp_yaml_plugin.YamlExporter'>}
```

!!! note "Entry-points example needs an installed plugin package"
    `load_plugins` runs, but it only finds plugins that third-party packages have registered under that group — so it isn't meaningfully run-verified in isolation here (the decorator registry above is). This is exactly how pytest, Flask, and many tools discover plugins: install a package, and it's automatically available with no code change in the host.

**Two discovery styles, summarized:**

- **Decorator/registry** — great *within* one codebase; plugins live in modules you import.
- **Entry points** — great *across* packages; third parties can extend your app just by `pip install`-ing their plugin. No import statement in your code.

There's also **directory scanning** (import every `.py` in a `plugins/` folder via `importlib`), but entry points are cleaner and the modern standard.

---

## Versioning and safety

Once third parties write plugins, you inherit responsibilities:

- **Version the contract.** If you change what `export()` must accept or return, old plugins break. Version your plugin API (e.g. a `PLUGIN_API_VERSION`) and refuse or warn on mismatches.
- **Fail gracefully.** One broken plugin shouldn't crash the host. Wrap `ep.load()` and each plugin call in try/except and log failures.
- **Trust boundaries.** A plugin is arbitrary code running in your process — it can do anything your app can. Only load plugins you trust. True sandboxing of untrusted plugins is hard (see the Security section's Sandboxing and Secure Plugin Systems topics).
- **Signature verification.** For plugins from outside sources, consider verifying a signature before loading, so you only run code from known publishers.

!!! warning "Plugins run with full privileges"
    Loading a plugin means executing its code inside your application. There's no built-in isolation — a malicious or buggy plugin can read your data, files, and secrets. Treat plugin sources like dependencies: vet them, pin versions, and for untrusted code use process/OS-level isolation rather than trying to sandbox within Python.

---

## When to build a plugin system

**Worth it when:**

- You genuinely need third parties (or separate teams) to extend the app without editing the core.
- There's a clear, stable extension point (like "an exporter" or "an auth backend").
- The set of extensions is open-ended and grows over time.

**Overkill when:**

- You have a fixed, known set of two or three variants — a simple `if`/dict is clearer.
- Nobody outside your team will ever add one.

!!! tip "Start with the registry, graduate to entry points"
    Begin with the in-code decorator registry. Only add entry-point discovery when you actually need external packages to plug in. The contract (the `Exporter` interface) stays the same either way.

---

## Practice exercises

1. Add an `XmlExporter` plugin without modifying `get_exporter`, and confirm it appears in `available`.
2. Make `get_exporter` return a default (e.g. JSON) instead of raising when the name is unknown, and decide which behavior is better for your use case.
3. Wrap plugin loading so one plugin raising on import doesn't stop the others; log which failed.
4. Add a `list_plugins()` function that returns each plugin's name and docstring for a `--help`-style listing.
5. Sketch a `PLUGIN_API_VERSION` check that refuses to load a plugin built against an incompatible contract version.
