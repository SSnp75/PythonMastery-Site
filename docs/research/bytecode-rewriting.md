---
title: Bytecode Rewriting
description: Runtime patching, instrumentation and bytecode manipulation
---

# Bytecode Rewriting <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>🔬 Research Track · Level 7</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Open-ended</span>
  </div>
</div>

---

## Why rewrite bytecode?

- Coverage tools (inject counting instructions)
- Profilers (trace function entries/exits)
- Security (sandbox dangerous operations)
- Optimization (remove redundant operations)

---

## Basic approach

```python
import types

def patch_function(func):
    code = func.__code__
    # Modify co_code, co_consts, etc.
    new_code = code.replace(co_consts=(None, 42))
    func.__code__ = new_code
```

---

<div class="pm-coming-soon">
<h3>📝 More sections coming</h3>
<p>bytecode library, code object surgery, safe patching patterns, real-world examples</p>
</div>
