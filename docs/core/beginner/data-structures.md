---
title: Data Structures
description: Lists, tuples, sets, dictionaries and when to use each
---

# Data Structures <span class="pm-badge pm-badge-beginner">Beginner</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 1</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="functions/">Functions</a></span>
  </div>
</div>

---

## Lists

Ordered, mutable, allows duplicates.

```python
fruits = ["apple", "banana", "cherry"]

# Access
fruits[0]     # "apple"
fruits[-1]    # "cherry"
fruits[1:3]   # ["banana", "cherry"]

# Mutate
fruits.append("date")
fruits.insert(1, "avocado")
fruits.remove("banana")
popped = fruits.pop()        # removes & returns last item

# Common operations
len(fruits)
sorted(fruits)
"apple" in fruits            # True (membership test)
fruits.index("cherry")       # find position
fruits.count("apple")        # count occurrences
```

### List comprehensions

```python
squares = [x**2 for x in range(10)]
evens   = [x for x in range(20) if x % 2 == 0]
matrix  = [[0]*3 for _ in range(3)]   # 3x3 grid
```

---

## Tuples

Ordered, **immutable**, allows duplicates.

```python
point = (3, 4)
x, y  = point            # unpacking

# Single-element tuple needs trailing comma
single = (42,)

# Use cases: fixed data, dictionary keys, function return values
def min_max(nums):
    return min(nums), max(nums)    # returns a tuple
```

---

## Sets

Unordered, mutable, **no duplicates**.

```python
colors = {"red", "green", "blue"}
colors.add("yellow")
colors.discard("red")

# Set operations
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

a | b    # union:        {1, 2, 3, 4, 5, 6}
a & b    # intersection: {3, 4}
a - b    # difference:   {1, 2}
a ^ b    # symmetric:    {1, 2, 5, 6}

# Fast membership testing
if "green" in colors:
    print("Found!")
```

---

## Dictionaries

Key-value pairs, ordered (3.7+), mutable, keys are unique.

```python
person = {
    "name": "Alice",
    "age": 30,
    "city": "NYC"
}

# Access
person["name"]                  # "Alice"
person.get("email", "N/A")     # "N/A" (safe access)

# Mutate
person["email"] = "a@b.com"    # add/update
del person["city"]             # delete
age = person.pop("age")        # remove & return

# Iterate
for key, value in person.items():
    print(f"{key}: {value}")

# Dict comprehension
squares = {x: x**2 for x in range(6)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
```

---

## When to use what

| Structure | Ordered | Mutable | Duplicates | Best for |
|---|---|---|---|---|
| `list` | Yes | Yes | Yes | General sequence, most common |
| `tuple` | Yes | No | Yes | Fixed data, dict keys, unpacking |
| `set` | No | Yes | No | Membership testing, deduplication |
| `dict` | Yes | Yes | Keys: No | Key-value lookup, JSON-like data |

---

## Nested structures

```python
# List of dicts — very common pattern
students = [
    {"name": "Alice", "grade": 95},
    {"name": "Bob", "grade": 87},
    {"name": "Charlie", "grade": 72},
]

# Sort by grade
top_students = sorted(students, key=lambda s: s["grade"], reverse=True)

# Dict of lists
schedule = {
    "Monday":    ["Math", "English"],
    "Tuesday":   ["Science", "Art"],
    "Wednesday": ["History", "PE"],
}
```

---

## Practice exercises

1. Remove all duplicates from a list while preserving order.
2. Write a function that counts word frequencies in a string (returns a dict).
3. Find the intersection of two lists without using `set()`.
4. Implement a simple phonebook using a dictionary with add, delete, search.
5. Given a list of `(name, score)` tuples, find the top 3 scores.
