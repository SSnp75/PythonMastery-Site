---
title: Control Flow
description: if/elif/else, for loops, while loops and match-case
---

# Control Flow <span class="pm-badge pm-badge-beginner">Beginner</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 1</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisite: <a href="python-basics/">Python Basics</a></span>
  </div>
</div>

---

## Conditionals

```python
score = 85

if score >= 90:
    print("A")
elif score >= 80:
    print("B")
elif score >= 70:
    print("C")
else:
    print("F")
```

### Ternary (one-liner)

```python
label = "pass" if score >= 50 else "fail"
```

### Truthy and Falsy values

```python
# Falsy: False, None, 0, 0.0, "", [], {}, set()
# Everything else is Truthy

if []:          print("never")     # empty list is falsy
if [1, 2, 3]:   print("yes!")      # non-empty list is truthy
if "":          print("never")     # empty string is falsy
if "hello":     print("yes!")
```

---

## for Loops

```python
# Iterate over a sequence
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# Range
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 10, 2):   # 2, 4, 6, 8
    print(i)

# Enumerate — get index AND value
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# Zip — iterate two lists together
names  = ["Alice", "Bob", "Charlie"]
scores = [95, 87, 72]
for name, score in zip(names, scores):
    print(f"{name}: {score}")
```

---

## while Loops

```python
count = 0
while count < 5:
    print(count)
    count += 1

# break — exit the loop early
while True:
    answer = input("Type 'quit' to exit: ")
    if answer == "quit":
        break
    print(f"You said: {answer}")

# continue — skip to next iteration
for i in range(10):
    if i % 2 == 0:
        continue        # skip even numbers
    print(i)            # prints 1, 3, 5, 7, 9
```

---

## match-case (Python 3.10+)

```python
command = "quit"

match command:
    case "quit":
        print("Quitting...")
    case "help":
        print("Showing help...")
    case "start" | "run":          # multiple patterns
        print("Starting...")
    case _:                        # default (wildcard)
        print(f"Unknown: {command}")
```

---

## Loop else clause

```python
# else runs only if the loop completed without break
for i in range(5):
    if i == 10:
        break
else:
    print("Loop finished normally")   # this prints
```

---

## Practice exercises

1. Write a program that prints all numbers 1–100. For multiples of 3 print "Fizz", multiples of 5 print "Buzz", multiples of both print "FizzBuzz".
2. Use a `while` loop to find the first power of 2 greater than 1000.
3. Write a number guessing game: generate a random number 1–100, let the user guess with "higher"/"lower" hints.
4. Use `match-case` to build a simple command dispatcher.
