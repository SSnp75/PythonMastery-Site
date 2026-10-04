---
title: PEG Parser Internals
description: CPython's PEG parser, the grammar file, packrat parsing theory, and a working toy PEG parser in Python
---

# PEG Parser Internals <span class="pm-badge pm-badge-research">Research</span>

<div class="pm-topic-header">
  <strong>🔬 Research Track · Level 7</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Open-ended</span>
    <span>📚 Prerequisite: <a href="../core/advanced/ast-manipulation/">AST Manipulation</a></span>
  </div>
</div>

---

## CPython's parser evolution

*CPython's parser evolution in PEG Parser Internals — what it is and when to use it.*

- **Python < 3.9** used an LL(1) parser — limited lookahead, which forced grammar hacks.
- **Python ≥ 3.9** uses a **PEG** (Parsing Expression Grammar) parser (PEP 617) — more
  expressive, with cleaner grammar rules and unlimited lookahead via backtracking.

The grammar lives in `Grammar/python.gram` in the CPython source and is compiled by the
`pegen` tool into the C parser.

---

## PEG vs. CFG — the key difference

*PEG vs. CFG — the key difference, part of PEG Parser Internals.*

A context-free grammar's `|` is **unordered** (ambiguity possible). A PEG's `/` is an
**ordered choice**: it tries alternatives left to right and commits to the first match. This
removes ambiguity by construction.

```
# PEG rule (ordered choice)
expr  <- term ('+' term)*
term  <- factor ('*' factor)*
factor<- NUMBER / '(' expr ')'
```

---

## Packrat parsing

*Memoize rule results per position to keep backtracking linear-time.*

PEG parsers can backtrack, which risks exponential time. **Packrat parsing** memoizes each
rule's result at each input position, making parsing linear time at the cost of memory. This
is the same `lru_cache`-style idea applied to parse positions.

---

## A working toy PEG parser

*A runnable recursive-descent parser with correct precedence.*

This recursive-descent parser evaluates arithmetic with correct precedence — the exact
structure CPython's generated parser uses, minus the memoization:

```python
import re

class PEG:
    def __init__(self, text):
        self.tokens = re.findall(r"\d+|[-+*/()]", text)
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, tok):
        if self.peek() == tok:
            self.pos += 1
            return True
        return False

    def expr(self):               # expr <- term (('+' / '-') term)*
        value = self.term()
        while self.peek() in ("+", "-"):
            op = self.tokens[self.pos]; self.pos += 1
            value = value + self.term() if op == "+" else value - self.term()
        return value

    def term(self):               # term <- factor (('*' / '/') factor)*
        value = self.factor()
        while self.peek() in ("*", "/"):
            op = self.tokens[self.pos]; self.pos += 1
            value = value * self.factor() if op == "*" else value // self.factor()
        return value

    def factor(self):             # factor <- NUMBER / '(' expr ')'
        if self.eat("("):
            value = self.expr()
            self.eat(")")
            return value
        tok = self.tokens[self.pos]; self.pos += 1
        return int(tok)

print(PEG("2 + 3 * 4").expr())       # 14  (precedence respected)
print(PEG("(2 + 3) * 4").expr())     # 20  (parentheses override)
```

---

## Modifying Python's own grammar

*Edit the grammar and regenerate CPython's parser.*

To add syntax to CPython you would: edit `Grammar/python.gram`, regenerate the parser with
`make regen-pegen`, and rebuild. This is how experimental syntax features are prototyped.

---

## Practice exercises

1. Add a `**` (power) rule to the toy parser with higher precedence than `*`.
2. Add unary minus so `-5 + 3` parses correctly.
3. Add packrat memoization: cache `(rule, pos)` results and confirm identical output.
4. Make `factor` raise a clear error on unexpected tokens instead of indexing past the end.
