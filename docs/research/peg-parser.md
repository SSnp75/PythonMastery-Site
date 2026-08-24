---
title: PEG Parser Internals
description: CPython's PEG parser, Grammar files and syntax modifications
---

# PEG Parser Internals <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>🔬 Research Track · Level 7</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Open-ended</span>
  </div>
</div>

---

## CPython's parser evolution

- Python < 3.9: LL(1) parser (limited, required hacks)
- Python >= 3.9: PEG parser (more expressive, cleaner grammar)

The grammar lives in `Grammar/python.gram` in the CPython source.

---

<div class="pm-coming-soon">
<h3>📝 More sections coming</h3>
<p>Reading the grammar, pegen tool, adding new syntax, packrat parsing theory</p>
</div>
