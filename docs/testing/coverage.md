---
title: Coverage & Mutation Testing
description: pytest-cov, branch coverage, mutation testing with mutmut and quality gates
---

# Coverage & Mutation Testing <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🧪 Testing Track · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 days</span>
    <span>📚 Prerequisite: <a href="pytest/">pytest</a></span>
  </div>
</div>

---

## Code coverage with pytest-cov

```bash
pip install pytest-cov

# Run with coverage
pytest --cov=src --cov-report=term-missing

# HTML report (visual)
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

Output:
```
----------- coverage: 6.5 -----------
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
src/calculator.py          25      3    88%   34-36
src/validator.py           40      8    80%   22-25, 51-54
src/utils.py               15      0   100%
-----------------------------------------------------
TOTAL                      80     11    86%
```

### Branch coverage (more thorough)

```bash
pytest --cov=src --cov-branch --cov-report=term-missing
```

Line coverage: "Was this line executed?"
Branch coverage: "Was every branch (if/else) taken both ways?"

```python
def categorize(age):
    if age < 18:
        return "minor"       # branch 1
    elif age < 65:
        return "adult"       # branch 2
    else:
        return "senior"      # branch 3

# To get 100% branch coverage, you need tests for ALL three paths
```

---

## Coverage configuration

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
branch = true
omit = ["tests/*", "*/migrations/*"]

[tool.coverage.report]
fail_under = 85      # CI fails if coverage drops below 85%
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.",
    "raise NotImplementedError",
    "pass",
]
```

---

## Mutation testing with mutmut

Coverage tells you **what code runs**. Mutation testing tells you **if your tests would catch bugs**.

It works by inserting small changes (mutations) into your code and checking if tests fail:

```bash
pip install mutmut

# Run mutation testing
mutmut run --paths-to-mutate=src/

# View results
mutmut results
mutmut show 5   # show specific surviving mutant
```

Example mutations:
```python
# Original
def is_adult(age):
    return age >= 18

# Mutant 1: change >= to >
def is_adult(age):
    return age > 18    # Would test_is_adult(18) catch this?

# Mutant 2: change 18 to 19
def is_adult(age):
    return age >= 19   # Would any test catch this?
```

If a mutant **survives** (tests still pass), your tests have a gap.

---

## Practice Exercises

1. **Achieve 100% branch coverage** for a function with nested if/else/elif.
2. **Run mutmut** on a simple module and kill all surviving mutants.
3. **Set up a coverage gate** in CI that fails the build below 90%.
4. **Find dead code** using coverage reports — code that's never executed.
