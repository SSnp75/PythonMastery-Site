---
title: "Lambda, reduce & Function Calls — Deep Dive"
description: Lambda pattern catalog, the full reduce toolbox, every way to call a function, and a complete string-methods reference
---

# Lambda, `reduce` & Function Calls <span class="pm-badge pm-badge-intermediate">Deep Dive</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="../core/intermediate/functional-programming/">Functional Programming</a></span>
  </div>
</div>

<div class="pm-next">
<strong>✅ Related</strong>
<a href="generators-decorators-filter.md">Generators, Decorators & Filtering</a>
<a href="../core/intermediate/functional-programming/">Functional Programming</a>
<a href="cheatsheets.md">Cheat Sheets</a>
</div>

---

A pattern catalog for `lambda`, a complete `reduce` toolbox, every way a callable can be
invoked, and a grouped reference of all `str` methods. Runnable examples show their output
inline.

---

## Lambda patterns

A `lambda` is a single-expression anonymous function. Reach for it when the logic is small
and passed directly to another function. Use a named `def` when logic is complex, needs
multiple statements, or benefits from a name/docstring.

### Higher-order lambdas

```python
apply_twice = lambda f, x: f(f(x))
make_adder  = lambda n: (lambda x: x + n)

print(apply_twice(lambda x: x + 1, 3))   # 5
add5 = make_adder(5)
print(add5(10))                           # 15
```

### Currying

```python
curried_add = lambda x: lambda y: x + y
print(curried_add(3)(4))   # 7
```

### Function composition

```python
compose = lambda f, g: lambda x: f(g(x))
inc = lambda x: x + 1
dbl = lambda x: x * 2
f = compose(dbl, inc)      # inc first, then dbl
print(f(5))                # 12
```

### Keys for sorting / min / max

```python
users = [{"name": "Bob", "age": 35}, {"name": "Alice", "age": 25}]
print(sorted(users, key=lambda u: u["age"])[0]["name"])   # Alice
print(max(users, key=lambda u: u["age"])["name"])         # Bob
```

### Ternary (conditional expression)

```python
parity = lambda x: "even" if x % 2 == 0 else "odd"
print(parity(4), parity(7))   # even odd
```

### Dispatch table

```python
ops = {
    "add": lambda a, b: a + b,
    "mul": lambda a, b: a * b,
}
print(ops["add"](3, 4))   # 7
print(ops["mul"](3, 4))   # 12
```

### Closures capturing outer variables

```python
def multiplier(n):
    return lambda x: x * n

triple = multiplier(3)
print(triple(10))   # 30
```

### The closure-in-a-loop gotcha

A lambda in a loop captures the **variable**, not its value. Bind it with a default argument.

```python
# Wrong: all funcs see the final n
bad = [lambda x: x + n for n in range(3)]
print([f(10) for f in bad])            # [12, 12, 12]

# Right: capture n per iteration
good = [lambda x, n=n: x + n for n in range(3)]
print([f(10) for f in good])           # [10, 11, 12]
```

### Delayed execution (thunk)

```python
thunk = lambda: sum(range(1000))   # nothing runs yet
print(thunk())                     # 499500  (runs on call)
```

### Exception-safe wrapper

```python
safe_div = lambda a, b: (a / b) if b else None
print(safe_div(10, 2))   # 5.0
print(safe_div(10, 0))   # None
```

### Lambda vs def

| Feature | lambda |
|---|---|
| Anonymous | ✔ |
| Single expression | ✔ |
| Multiple statements | ✘ |
| Docstring | ✘ |
| Best for | small inline logic |

---

## The `reduce` toolbox

`reduce(func, iterable[, initializer])` folds an iterable into a single value by applying a
two-argument function cumulatively.

```python
from functools import reduce
```

### Arithmetic

```python
from functools import reduce

print(reduce(lambda a, b: a + b, [1, 2, 3, 4]))         # 10
print(reduce(lambda a, b: a * b, [1, 2, 3, 4]))         # 24
print(reduce(lambda a, b: a if a < b else b, [5, 2, 9, 1]))   # 1 (min)
```

### With an initializer

The initializer is the starting accumulator and the result for an empty iterable.

```python
from functools import reduce

print(reduce(lambda a, b: a + b, [], 10))   # 10  (safe on empty input)
```

### Strings

```python
from functools import reduce

print(reduce(lambda a, b: a + b, ["Py", "thon", "3"]))        # Python3
print(reduce(lambda a, b: f"{a}, {b}", ["a", "b", "c"]))      # a, b, c
```

### Lists & sets

```python
from functools import reduce

print(reduce(lambda a, b: a + b, [[1, 2], [3, 4], [5]]))      # [1, 2, 3, 4, 5]
print(reduce(lambda a, b: a & b, [{1, 2, 3}, {2, 3}, {3, 4}]))  # {3}
print(reduce(lambda a, b: a | b, [{1, 2}, {2, 3}, {3, 4}]))     # {1, 2, 3, 4}
```

### Dictionaries

```python
from functools import reduce

merged = reduce(lambda a, b: {**a, **b}, [{"a": 1}, {"b": 2}, {"c": 3}])
print(merged)   # {'a': 1, 'b': 2, 'c': 3}

# Frequency count (right-hand dict wins on key overlap)
freq = reduce(lambda acc, x: acc | {x: acc.get(x, 0) + 1}, "banana", {})
print(freq)     # {'b': 1, 'a': 3, 'n': 2}
```

### Booleans

```python
from functools import reduce

print(reduce(lambda a, b: a and b, [True, True, False]))   # False  (all)
print(reduce(lambda a, b: a or b, [False, False, True]))   # True   (any)
```

### Multi-value accumulators

```python
from functools import reduce

nums = [10, 20, 30]
total, count = reduce(lambda acc, x: (acc[0] + x, acc[1] + 1), nums, (0, 0))
print(total / count)   # 20.0

# min, max, sum in a single pass
lo, hi, s = reduce(
    lambda acc, x: (min(acc[0], x), max(acc[1], x), acc[2] + x),
    [5, 2, 9, 1],
    (float("inf"), float("-inf"), 0),
)
print((lo, hi, s))   # (1, 9, 17)
```

### Composition pipeline

```python
from functools import reduce

funcs = [lambda x: x + 2, lambda x: x * 3, lambda x: x - 5]
pipeline = reduce(lambda f, g: lambda x: g(f(x)), funcs)
print(pipeline(10))   # ((10 + 2) * 3) - 5 = 31
```

### State machine (finite automaton)

```python
from functools import reduce

transitions = {
    ("start", "a"): "middle",
    ("middle", "b"): "end",
}
end = reduce(
    lambda state, char: transitions.get((state, char), state),
    "ab",
    "start",
)
print(end)   # end
```

### Tree flatten (nested lists)

```python
from functools import reduce

def flatten(acc, x):
    if isinstance(x, list):
        return reduce(flatten, x, acc)
    return acc + [x]

print(reduce(flatten, [1, [2, 3], [4, [5]]], []))   # [1, 2, 3, 4, 5]
```

### Object building

```python
from functools import reduce

print(reduce(lambda a, b: b + a, "abcd"))              # dcba (reverse)
print(reduce(lambda a, b: a * 10 + b, [1, 2, 3, 4]))   # 1234 (digits -> number)
```

### Math algorithms

```python
from functools import reduce
from math import gcd

print(reduce(gcd, [48, 64, 16]))                               # 16
print(reduce(lambda a, b: a * b // gcd(a, b), [4, 6, 8]))      # 24 (lcm)
```

### `reduce` usage map

| Category | Examples |
|---|---|
| Arithmetic | sum, product, min, max |
| Initializer | safe defaults, empty-input baseline |
| Strings | concatenation, join-with-separator |
| Lists / sets | flatten, union, intersection |
| Dictionaries | merge, frequency count |
| Booleans | all (`and`), any (`or`) |
| Custom aggregation | multi-value accumulators (avg, min/max/sum) |
| Functional | composition, pipelines |
| State machines | transition tables, automata |
| Trees | nested flattening |
| Object building | reverse string, build number from digits |
| Math | gcd, lcm, dot product |

!!! tip "When not to use reduce"
    For plain sums use `sum()`; for min/max use `min()`/`max()`. `reduce` shines for custom
    folds (accumulators, state machines, composition) where no built-in fits. A readable
    `for` loop often beats a clever `reduce` one-liner.

---

## A composable `Pipeline` class

A small reusable class that chains callables left to right, supports `|` chaining, and can
compose right to left.

```python
from functools import reduce

class Pipeline:
    def __init__(self, steps=None):
        self.steps = list(steps or [])

    def add(self, fn):
        self.steps.append(fn)
        return self

    def __or__(self, fn):            # p | fn
        return Pipeline(self.steps + [fn])

    def __call__(self, x):           # left-to-right
        return reduce(lambda acc, fn: fn(acc), self.steps, x)

    def compose(self):               # right-to-left callable
        return lambda x: reduce(lambda acc, fn: fn(acc), reversed(self.steps), x)

# Construct with a list
p = Pipeline([lambda x: x + 2, lambda x: x * 3, lambda x: x - 5])
print(p(10))              # 31

# Operator chaining
p2 = Pipeline() | (lambda x: x + 2) | (lambda x: x * 3) | (lambda x: x - 5)
print(p2(10))             # 31

# Add dynamically
p3 = Pipeline()
p3.add(lambda x: x + 1).add(lambda x: x * 10)
print(p3(5))              # 60

# Right-to-left composition
print(p.compose()(10))    # ((10 - 5) * 3) + 2 = 17
```

---

## Every way to call a function

| Call type | Example |
|---|---|
| Direct | `print()` |
| Positional args | `pow(2, 3)` |
| Keyword args | `round(3.1415, ndigits=2)` |
| Mixed | `f(1, b=2)` |
| Via variable (alias) | `alias = len; alias("abc")` |
| Returned by a function | `outer()()` |
| From a data structure | `ops["add"](3, 4)` |
| Lambda, called inline | `(lambda x: x + 1)(5)` |
| `*args` unpacking | `f(*[1, 2, 3])` |
| `**kwargs` unpacking | `dict(**{"a": 1, "b": 2})` |
| Instance method | `"hello".upper()` |
| Class method | `dict.fromkeys(["a", "b"])` |
| Static method | `math.sqrt(16)` |
| Callable object | `obj()` where `obj.__call__` exists |
| `getattr` dynamic | `getattr(str, "lower")("ABC")` |
| Decorator-wrapped | `@lru_cache` then `fib(10)` |
| `map` / `filter` | `list(map(int, ["1", "2"]))` |
| `reduce` | `reduce(lambda a, b: a + b, [1, 2, 3])` |
| Partial application | `partial(pow, 2)(8)` |
| Recursion | `fact(n - 1)` |
| Async | `await asyncio.sleep(1)` |
| Async gather | `await asyncio.gather(f1(), f2())` |
| Thread | `Thread(target=f).start()` |
| Process | `Process(target=f).start()` |
| `eval` / `exec` | `eval("1 + 2")`, `exec("x = 5")` |
| `globals()` lookup | `globals()["len"]([1, 2])` |
| `operator.methodcaller` | `methodcaller("upper")("hi")` |
| `inspect` | `inspect.signature(f)` |
| `ctypes` / FFI | `CDLL("m.so").add(2, 3)` |
| `multiprocessing.Pool` | `pool.map(str.upper, ["a", "b"])` |
| `concurrent.futures` | `executor.submit(pow, 2, 8)` |
| `asyncio.to_thread` | `await asyncio.to_thread(sum, [1, 2, 3])` |
| Timer / scheduled | `Timer(2, print, args=("done",)).start()` |
| Callback / hook | `button.set_callback(on_press)` |
| Reflection | `getattr(math, "cos")(0)` |

A few of these verified live:

```python
from functools import partial, reduce
from operator import methodcaller

print(partial(pow, 2)(8))                        # 256
print(methodcaller("upper")("hi"))               # HI
print(getattr(str, "lower")("ABC"))              # abc
print(list(map(int, ["1", "2"])))                # [1, 2]
print(list(filter(str.isalpha, "a1b2")))         # ['a', 'b']
print(reduce(lambda a, b: a + b, [1, 2, 3]))     # 6

def greet():
    return "hi"
print(globals()["greet"]())                      # hi  (globals holds module-level names)
```

!!! note "`globals()` vs builtins"
    `globals()` holds names defined at module level, so `globals()["greet"]` works but
    `globals()["len"]` raises `KeyError` — `len` is a builtin. Reach builtins via
    `__builtins__` or `import builtins; builtins.len`.

---

## Complete string-methods reference

Grouped list of every `str` method. (`ord`/`chr` are built-in functions, not methods, but
belong in the same mental bucket.)

### Case conversion

| Method | Does |
|---|---|
| `upper()` | all uppercase |
| `lower()` | all lowercase |
| `casefold()` | aggressive lowercase (Unicode-safe comparisons) |
| `capitalize()` | first char upper, rest lower |
| `title()` | title-case each word |
| `swapcase()` | swap upper ↔ lower |

### Searching & checking

| Method | Does |
|---|---|
| `startswith(x)` | starts with `x` |
| `endswith(x)` | ends with `x` |
| `find(x)` | index of `x`, or `-1` |
| `rfind(x)` | rightmost `find` |
| `index(x)` | like `find`, raises if missing |
| `rindex(x)` | rightmost `index` |
| `count(x)` | number of occurrences |

### Validation (`is*`)

| Method | True when |
|---|---|
| `isalnum()` | alphanumeric |
| `isalpha()` | alphabetic |
| `isdigit()` | digits |
| `isdecimal()` | decimal chars |
| `isnumeric()` | numeric chars |
| `isidentifier()` | valid Python identifier |
| `islower()` | all lowercase |
| `isupper()` | all uppercase |
| `istitle()` | title-cased |
| `isspace()` | whitespace only |
| `isprintable()` | printable chars |
| `isascii()` | ASCII only |

### Trimming

| Method | Does |
|---|---|
| `strip(chars)` | trim both ends |
| `lstrip(chars)` | trim left |
| `rstrip(chars)` | trim right |
| `removeprefix(p)` | remove exact prefix |
| `removesuffix(s)` | remove exact suffix |

!!! warning "strip takes a character set, not a substring"
    `"abcxyz".strip("abc")` removes any of `a`, `b`, `c` from both ends — it does not
    remove the substring `"abc"`. Use `removeprefix` / `removesuffix` for exact affixes.

### Splitting & joining

| Method | Does |
|---|---|
| `split(sep)` | split into a list |
| `rsplit(sep)` | split from the right |
| `splitlines()` | split on line boundaries |
| `partition(sep)` | → `(before, sep, after)` |
| `rpartition(sep)` | partition from the right |
| `sep.join(it)` | join an iterable with `sep` |

### Replacing & formatting

| Method | Does |
|---|---|
| `replace(a, b)` | replace substring |
| `format(...)` | advanced formatting |
| `format_map(m)` | format from a mapping |
| `str.maketrans(...)` | build a translation table |
| `translate(table)` | apply a translation table |

### Encoding, alignment, padding

| Method | Does |
|---|---|
| `encode(enc)` | encode to `bytes` |
| `center(w)` | center within width |
| `ljust(w)` | left-justify |
| `rjust(w)` | right-justify |
| `zfill(w)` | zero-pad on the left |

### A few in action

```python
print("  Hello World  ".strip())                 # Hello World
print("a,b,c".split(","))                         # ['a', 'b', 'c']
print("-".join(["2026", "01", "15"]))             # 2026-01-15
print("key=value".partition("="))                 # ('key', '=', 'value')
print("https://x".removeprefix("https://"))       # x
print("42".zfill(5))                               # 00042
print("ABC".casefold())                            # abc
table = str.maketrans("abc", "xyz")
print("cab".translate(table))                      # zxy
```

### Three ways to format

```python
var = "Tom"
print("the variable is %s" % var)          # the variable is Tom
print("pi is {:.2f}".format(3.14159))       # pi is 3.14
print(f"the variable is {var}")             # the variable is Tom
```

!!! tip "Build strings with join, not `+=` in a loop"
    Repeated `s += x` in a loop is O(n²) because strings are immutable. `"".join(parts)`
    builds the result in one pass and is dramatically faster for large inputs.

---

## Practice exercises

1. Write a `compose(*fns)` using `reduce` that composes any number of functions left to right.
2. Use `reduce` to count word frequencies in a sentence into a dict.
3. Rewrite a nested-loop sum of a deeply nested list using the `flatten` reducer.
4. Extend `Pipeline` with a `__repr__` that lists the number of steps.
5. Given a list of filenames, keep only those ending in `.py` and strip the extension, using `filter` + `map` + string methods.
6. Build a dispatch table of lambdas for `+ - * /` and evaluate `("*", 6, 7)`.
