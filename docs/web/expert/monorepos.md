---
title: "Monorepos"
description: Structure, tooling, dependency management and CI for a single repository holding many projects
---

# Monorepos <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🌐 Web & APIs Track · Level 6</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisites: <a href="../competent/packaging/">Python Packaging</a>, <a href="../../deployment/cicd/">CI/CD</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What a monorepo is and the problem it solves
- [x] How to structure a Python monorepo
- [x] Manage shared dependencies across projects
- [x] Run CI efficiently (only build what changed)
- [x] Weigh monorepo vs polyrepo honestly

!!! note "This is a structural/tooling topic"
    Monorepos are about repository layout, dependency management, and CI configuration rather than a single runnable script. The examples here are directory layouts and config snippets, not executable Python.

---

## What is a monorepo?

A **monorepo** (monolithic repository) is a single version-control repository that holds **many projects** — multiple services, shared libraries, tooling — instead of splitting each into its own repo (the **polyrepo** approach).

```
   Polyrepo                         Monorepo
   ┌──────────┐ ┌──────────┐        ┌─────────────────────────┐
   │ repo:api │ │ repo:web │        │ one repo                 │
   └──────────┘ └──────────┘        │  ├── services/api        │
   ┌──────────┐ ┌──────────┐        │  ├── services/web        │
   │repo:core │ │repo:utils│        │  ├── libs/core           │
   └──────────┘ └──────────┘        │  └── libs/utils          │
   4 repos, 4 histories             └─────────────────────────┘
                                     1 repo, 1 history
```

Google, Meta, and Microsoft run enormous monorepos. The appeal isn't scale for its own sake — it's **atomic change**: you can update a shared library and every service that uses it in a single commit, with one review and one CI run.

---

## Typical Python monorepo structure

```
myorg/
├── pyproject.toml            # workspace root config
├── libs/                     # shared, reusable packages
│   ├── core/
│   │   ├── pyproject.toml
│   │   └── src/core/...
│   └── auth/
│       ├── pyproject.toml
│       └── src/auth/...
├── services/                 # deployable applications
│   ├── api/
│   │   ├── pyproject.toml     # depends on libs/core, libs/auth
│   │   └── src/api/...
│   └── worker/
│       ├── pyproject.toml
│       └── src/worker/...
├── tools/                    # internal scripts, generators
└── .github/workflows/ci.yml  # shared CI
```

**The principle:** each `libs/*` and `services/*` is its own installable package with its own `pyproject.toml`, but they live and version together in one repo. A service declares a dependency on a shared lib, and the tooling links them locally.

---

## Dependency management

The key trick is letting one package in the repo depend on another **by local path**, so changes are picked up immediately without publishing to PyPI.

### uv workspaces (modern, fast)

`uv` has first-class workspace support. The root `pyproject.toml` declares members:

```toml
# root pyproject.toml
[tool.uv.workspace]
members = ["libs/*", "services/*"]
```

A service depends on a shared lib as a workspace source:

```toml
# services/api/pyproject.toml
[project]
name = "api"
dependencies = ["core", "auth"]

[tool.uv.sources]
core = { workspace = true }
auth = { workspace = true }
```

Now `core` resolves to `libs/core` in the same repo. Edit the lib, and the service sees the change instantly — no reinstall, no version bump, no publish.

### Other options

- **Poetry** — `path` dependencies (`core = { path = "../../libs/core", develop = true }`) achieve the same local linking.
- **Editable installs** — plain pip with `pip install -e libs/core` links packages during development.
- **Pants / Bazel** — full build systems designed for large monorepos; they add fine-grained dependency graphs and caching but bring significant setup cost. Reach for these only at real scale.

!!! tip "Start simple"
    For a handful of packages, uv workspaces (or Poetry path deps) are plenty. Bazel/Pants pay off at hundreds of packages and large teams — not before.

---

## CI: only build what changed

The naive monorepo CI rebuilds and tests *everything* on every commit — which gets slow as the repo grows. The fix is **change detection**: run CI only for the packages a commit actually touched (and their dependents).

Illustrative GitHub Actions using path filters:

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      api: ${{ steps.filter.outputs.api }}
      core: ${{ steps.filter.outputs.core }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            api:  ['services/api/**', 'libs/core/**']
            core: ['libs/core/**']

  test-api:
    needs: changes
    if: ${{ needs.changes.outputs.api == 'true' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: uv run --package api pytest
```

Notice the `api` filter includes `libs/core/**`: if the shared lib changes, the API that depends on it is retested too. Getting this dependency mapping right is the heart of efficient monorepo CI. At larger scale, build systems (Bazel/Pants) compute this dependency graph automatically instead of you maintaining path filters by hand.

---

## Monorepo vs polyrepo — the honest tradeoff

| | **Monorepo** | **Polyrepo** |
|---|---|---|
| Cross-project changes | Atomic — one commit, one PR | Coordinated across repos, painful |
| Code sharing | Trivial (local path deps) | Publish/version each shared lib |
| Visibility | Everything in one place | Scattered |
| Access control | Coarse (whole repo) | Fine (per repo) |
| CI complexity | Needs change detection | Simple per repo |
| Tooling at scale | May need Bazel/Pants | Standard tooling |
| Clone size / speed | Grows large | Small per repo |

**Choose a monorepo when:** projects share a lot of code, change together, and one team (or closely coordinated teams) owns them. The atomic-change and code-sharing wins are large.

**Choose polyrepo when:** projects are independent, owned by separate teams with different release cadences, or need strict per-project access control.

!!! warning "A monorepo is not automatically simpler"
    It trades many small problems (coordinating changes across repos) for a few big ones (CI change-detection, clone size, coarse access control). It shines when projects are genuinely coupled and share code; it adds friction when they're independent. Pick based on how your projects actually relate — not on what big tech companies do at a scale you don't have.

---

## Practice exercises

1. Sketch a monorepo layout for a project with two services and one shared library; write the `pyproject.toml` dependency links using uv workspaces.
2. Write CI path filters so that a change to `libs/core` retests both services that depend on it, but a change to `services/api` retests only the API.
3. List three concrete pain points you'd hit maintaining the same code as three separate repos, and how a monorepo removes each.
4. Argue the opposite: describe a project where polyrepo is clearly the better choice, and why.
5. Research one large-scale monorepo tool (Bazel or Pants) and note the specific problem it solves that path-filter CI does not.
