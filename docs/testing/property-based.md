---
title: Property-Based Testing
description: Hypothesis library, strategies, stateful testing and finding edge cases automatically
---

# Property-Based Testing <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🧪 Testing Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisite: <a href="pytest/">pytest</a></span>
  </div>
</div>

---

## What is property-based testing?

Instead of writing specific test cases, you describe **properties** that should always hold, and the framework generates hundreds of random inputs to find violations.

```python
from hypothesis import given
from hypothesis import strategies as st

# Property: reversing a list twice gives the original
@given(st.lists(st.integers()))
def test_reverse_twice_is_identity(lst):
    assert list(reversed(list(reversed(lst)))) == lst

# Property: sorting is idempotent
@given(st.lists(st.integers()))
def test_sort_is_idempotent(lst):
    sorted_once = sorted(lst)
    sorted_twice = sorted(sorted_once)
    assert sorted_once == sorted_twice

# Property: length preserved after sort
@given(st.lists(st.integers()))
def test_sort_preserves_length(lst):
    assert len(sorted(lst)) == len(lst)
```

Hypothesis will test with hundreds of random lists including: empty, single element, duplicates, negative numbers, very large numbers, etc.

---

## Strategies — generating test data

```python
from hypothesis import strategies as st

# Basic types
st.integers()                    # any int
st.integers(min_value=0, max_value=100)
st.floats(allow_nan=False)       # floats without NaN
st.text(min_size=1, max_size=50) # non-empty strings
st.booleans()
st.none()

# Collections
st.lists(st.integers(), min_size=1, max_size=20)
st.dictionaries(st.text(min_size=1), st.integers())
st.tuples(st.integers(), st.text())
st.frozensets(st.integers())

# Composite (custom data)
@st.composite
def user_strategy(draw):
    name = draw(st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=("L",))))
    age = draw(st.integers(min_value=0, max_value=150))
    email = draw(st.emails())
    return {"name": name, "age": age, "email": email}

@given(user_strategy())
def test_user_creation(user_data):
    user = create_user(**user_data)
    assert user.name == user_data["name"]
```

---

## Finding real bugs

```python
from hypothesis import given
from hypothesis import strategies as st

def encode(text: str) -> str:
    """Run-length encoding."""
    if not text:
        return ""
    result = []
    count = 1
    for i in range(1, len(text)):
        if text[i] == text[i-1]:
            count += 1
        else:
            result.append(f"{count}{text[i-1]}")
            count = 1
    result.append(f"{count}{text[-1]}")
    return "".join(result)

def decode(encoded: str) -> str:
    """Decode run-length encoding."""
    result = []
    i = 0
    while i < len(encoded):
        count = ""
        while i < len(encoded) and encoded[i].isdigit():
            count += encoded[i]
            i += 1
        result.append(encoded[i] * int(count))
        i += 1
    return "".join(result)

# Property: encode then decode gives back the original
@given(st.text(alphabet="abcdef", min_size=1))
def test_encode_decode_roundtrip(text):
    assert decode(encode(text)) == text

# Hypothesis might find: text with digits breaks the decoder!
# e.g., encode("a3b") → "1a131b" → decode gives wrong result
```

---

## Practice Exercises

1. **Test a JSON serializer** — property: `json.loads(json.dumps(x)) == x` for various types.
2. **Test a sort function** — properties: idempotent, preserves length, every element from input appears in output.
3. **Find a bug** in a function using Hypothesis that you wouldn't find with manual test cases.
4. **Write a composite strategy** for generating valid database records.
5. **Use `@example`** to pin a known regression alongside random testing.
