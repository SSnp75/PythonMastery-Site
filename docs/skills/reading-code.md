---
title: Reading Other People's Code
description: Strategies for understanding unfamiliar codebases efficiently
---

# Reading Other People's Code <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🧠 Soft Skills · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 days</span>
  </div>
</div>

---

## The systematic approach

### 1. Start from the entry point

```
What runs first?
├── main.py / __main__.py
├── app = FastAPI() → which routes?
├── if __name__ == "__main__" → what's called?
└── CLI entry point (pyproject.toml scripts)
```

### 2. Read tests first

Tests tell you:
- What the code is **supposed to do**
- What inputs/outputs look like
- Edge cases the author considered
- How to use the API

### 3. Map the architecture

```
┌── Read folder structure (what's the organization?)
├── Read imports (what depends on what?)
├── Find the domain objects (models, entities)
├── Find the entry points (routes, CLI, jobs)
└── Find the data flow (input → process → output)
```

### 4. Use tools

```bash
# Find where something is defined
grep -rn "class UserService" src/

# Find all usages of a function
grep -rn "create_user" src/

# Understand dependencies
pip show package_name   # what it does
pipdeptree              # dependency tree

# Generate call graph
pyan3 src/**/*.py --dot | dot -Tpng -o callgraph.png
```

---

## Strategies for different situations

| Situation | Strategy |
|---|---|
| Bug to fix | Start from the error, trace backwards |
| New feature | Find similar feature, see how it's done |
| PR review | Read tests first, then implementation |
| New codebase | README → tests → entry point → domain models |
| Legacy code | Add logging/breakpoints, observe behavior |

---

## Practice Exercises

1. **Clone a popular library** (requests, click, flask) and trace a simple operation through the code.
2. **Read a PR** on a project you use — understand the change without context.
3. **Map the architecture** of a Django/FastAPI project by only reading file structure and imports.
4. **Add a feature** to an unfamiliar open-source project (start with "good first issue" labels).
