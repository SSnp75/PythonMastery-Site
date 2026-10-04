---
title: Python Basics
description: Variables, data types, operators and your first Python programs
---

# Python Basics <span class="pm-badge pm-badge-beginner">Beginner</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 1</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 No prerequisites</span>
  </div>
</div>

<div class="pm-next">
<strong>✅ What's next after this</strong>
<a href="control-flow/">Control Flow</a>
<a href="functions/">Functions</a>
</div>

---

!!! info "When you'd use this"
    Variables, data types, operators and your first Python programs.

    Reach for these fundamentals on day one of any script: declaring variables, converting user input, doing arithmetic, and formatting output.


## What you'll learn

- [x] Install Python and run your first script
- [x] Understand variables and naming rules
- [x] Work with all basic data types
- [x] Use arithmetic, comparison and logical operators
- [x] Get input from the user and format output
- [x] Understand how Python executes code line by line

---

## Variables & Data Types

*Store values in named variables; every value has a type (`str`, `int`, `float`, `bool`, `None`). Use `type()` and conversions when data crosses boundaries like user input.*

Python is dynamically typed — you don't declare types, you just assign values.

```python
# Basic types
name    = "Alice"        # str
age     = 30             # int
height  = 1.75           # float
is_dev  = True           # bool
nothing = None           # NoneType

# Check the type
print(type(name))        # <class 'str'>
print(type(age))         # <class 'int'>
```

### Type conversion

```python
x = "42"
print(int(x))       # 42      (str → int)
print(float(x))     # 42.0    (str → float)
print(str(123))     # '123'   (int → str)
print(bool(0))      # False   (int → bool)
print(bool("hi"))   # True    (any non-empty string is truthy)
```

---

## Operators

*Arithmetic, comparison, and logical operators are the building blocks of every expression. Note `/` always gives a float and `//` floors; comparisons/logic return booleans for conditions.*

```python
# Arithmetic
10 + 3   # 13
10 - 3   # 7
10 * 3   # 30
10 / 3   # 3.333...  (always float)
10 // 3  # 3         (floor division)
10 % 3   # 1         (remainder)
2 ** 8   # 256       (power)

# Comparison  — all return bool
5 > 3    # True
5 == 5   # True
5 != 4   # True
5 >= 5   # True

# Logical
True and False  # False
True or False   # True
not True        # False
```

---

## Strings

*Text values with rich methods and slicing. Reach for f-strings to build output and `.upper()`/`.split()`/`.replace()` etc. for everyday text work.*

```python
# Creation
s1 = 'single quotes'
s2 = "double quotes"
s3 = """multi
line"""

# f-strings (use these — they're the modern way)
name = "Alice"
age  = 30
msg  = f"Hello, {name}! You are {age} years old."

# Common operations
s = "Hello, World!"
print(len(s))           # 13
print(s.upper())        # HELLO, WORLD!
print(s.lower())        # hello, world!
print(s.replace("World", "Python"))  # Hello, Python!
print(s.split(", "))    # ['Hello', 'World!']
print(s[0:5])           # Hello    (slicing)
print(s[-6:])           # World!
```

---

## Input & Output

*`print` sends text out; `input` reads a line in (always as a string — convert it immediately). The basics of any interactive script.*

```python
# Output
print("Hello")
print(f"Value: {42:.2f}")   # Value: 42.00

# Input (always returns a string)
name = input("What is your name? ")
age  = int(input("How old are you? "))   # convert immediately
```

---

## Your first program

*Putting it together: read input, compute, print output — the shape of countless small scripts.*

```python
# greeting.py
name = input("Enter your name: ")
age  = int(input("Enter your age: "))

print(f"Hello, {name}!")
print(f"In 10 years you will be {age + 10}.")
```

Run it:
```bash
python greeting.py
```

---

## Key rules to remember

*Key rules to remember in Python Basics — what it is and when to use it.*

!!! tip "Python Style"
    - Use `snake_case` for variable names: `first_name`, not `firstName`
    - Use 4 spaces for indentation (never tabs)
    - Lines should stay under 79 characters
    - These are [PEP 8](https://peps.python.org/pep-0008/) conventions — follow them from day one

---

## Practice exercises

1. Write a program that asks for two numbers and prints their sum, difference, product and quotient.
2. Ask the user for their name and birth year, then print how old they are.
3. Create variables of every data type and print them with `type()`.
4. Write a temperature converter: Celsius → Fahrenheit using `F = C * 9/5 + 32`.
