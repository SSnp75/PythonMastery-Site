---
title: Glossary
description: Every Python and computing term used across the site, defined in plain language — from ABC to WSGI
---

# 📖 Glossary

Python and computing terms defined in plain language. Use `Ctrl+F` (or the search bar) to jump to a term.

---

## A

*A in Glossary — what it is and when to use it.*

**ABC** — Abstract Base Class. A class that can't be instantiated directly; used to define an interface subclasses must implement.

**Argument** — A value passed into a function when you call it. Compare *parameter* (the name in the definition).

**AST** — Abstract Syntax Tree. A tree representation of source code structure, produced by `ast.parse()` and used by tools that analyze or transform code.

**Async / await** — Keywords for cooperative concurrency. `async def` defines a coroutine; `await` suspends it until an awaitable completes.

**Asyncio** — The standard-library framework for single-threaded concurrency using an event loop and coroutines.

**Attribute** — A value or method bound to an object, accessed with dot notation (`obj.name`).

## B

*B in Glossary — what it is and when to use it.*

**Big-O** — Notation describing how an algorithm's time or space grows with input size (e.g. O(n), O(n log n)).

**Bytecode** — The low-level instructions Python source is compiled to before the interpreter executes them. Inspect with `dis`.

**bool** — The boolean type, `True` or `False`. A subclass of `int`.

## C

*C in Glossary — what it is and when to use it.*

**Callable** — Any object you can invoke with `()` — functions, methods, classes, or objects defining `__call__`.

**Class** — A blueprint for creating objects, bundling data (attributes) and behavior (methods).

**Closure** — A function that remembers variables from its enclosing scope even after that scope has finished.

**Comprehension** — Concise syntax to build a list, dict, set, or generator from an iterable: `[x for x in xs]`.

**Context manager** — An object usable with `with` that sets up and tears down a resource via `__enter__`/`__exit__`.

**Coroutine** — An async function (defined with `async def`) that can be paused and resumed by the event loop.

**CPython** — The reference implementation of Python, written in C. The default interpreter most people run.

**CRDT** — Conflict-free Replicated Data Type. A data structure that merges concurrent edits across nodes without coordination.

## D

*D in Glossary — what it is and when to use it.*

**Dataclass** — A class auto-generating `__init__`, `__repr__`, and more from annotated fields via `@dataclass`.

**Decorator** — A callable that wraps another function or class to modify its behavior. Applied with `@`.

**Dependency injection** — Supplying an object's dependencies from outside rather than creating them internally; eases testing.

**Descriptor** — An object defining `__get__`, `__set__`, or `__delete__` that controls attribute access on its owner class.

**Dict** — The built-in hash-map type mapping keys to values. Insertion-ordered since Python 3.7.

**Duck typing** — Using objects by their behavior rather than their type: "if it quacks like a duck, treat it as one."

**Dunder** — A "double underscore" special method like `__init__` or `__len__` that hooks into language syntax.

## E

*E in Glossary — what it is and when to use it.*

**EAFP** — Easier to Ask Forgiveness than Permission. Try the operation and handle the exception if it fails.

**Event loop** — The core of asyncio: it schedules and runs coroutines, resuming each when its awaited work is ready.

**Exception** — An error signal raised during execution, caught with `try`/`except`.

## F

*F in Glossary — what it is and when to use it.*

**f-string** — A formatted string literal, `f"{value}"`, that embeds expressions directly in the string.

**First-class function** — The property that functions can be passed around, returned, and stored like any value.

**Future** — A placeholder for a result that will be available later, used in async and concurrent code.

## G

*G in Glossary — what it is and when to use it.*

**Garbage collection** — Automatic memory reclamation. CPython uses reference counting plus a cyclic collector.

**Generator** — A function using `yield` to produce values lazily, one at a time, keeping its state between calls.

**GIL** — Global Interpreter Lock. Lets only one thread execute Python bytecode at a time in CPython.

## H

*H in Glossary — what it is and when to use it.*

**Hashable** — An object with a stable `__hash__`, allowing it to be a dict key or set member (e.g. tuples, strings).

**Higher-order function** — A function that takes or returns other functions (`map`, `sorted(key=...)`).

## I

*I in Glossary — what it is and when to use it.*

**Immutable** — Cannot be changed after creation (tuples, strings, frozensets). Opposite of *mutable*.

**Import system** — The machinery that finds, loads, and caches modules when you `import` them.

**Iterable** — Any object you can loop over (`list`, `dict`, file, generator) — it provides an iterator via `__iter__`.

**Iterator** — An object with `__next__()` that yields values one at a time until it raises `StopIteration`.

## J

*J in Glossary — what it is and when to use it.*

**JIT** — Just-In-Time compilation. Compiling code to machine code at runtime for speed (Numba, PyPy).

**JSON** — JavaScript Object Notation. A text data format; handled by the `json` module.

## K

*K in Glossary — what it is and when to use it.*

**Keyword argument** — An argument passed by name, `f(timeout=5)`, rather than by position.

## L

*L in Glossary — what it is and when to use it.*

**Lambda** — A small anonymous function written inline: `lambda x: x + 1`.

**LBYL** — Look Before You Leap. Check preconditions before acting (opposite of EAFP).

**List** — The built-in ordered, mutable sequence type.

**lru_cache** — A `functools` decorator that memoizes a function's results with a least-recently-used cache.

## M

*M in Glossary — what it is and when to use it.*

**Metaclass** — The "class of a class." Controls how classes themselves are created (`type` is the default).

**Method** — A function defined inside a class and bound to its instances.

**Module** — A single `.py` file of reusable code. A *package* is a directory of modules.

**MRO** — Method Resolution Order. The sequence Python searches for an attribute across an inheritance hierarchy.

**Mutable** — Can be changed in place after creation (lists, dicts, sets).

## N

*N in Glossary — what it is and when to use it.*

**Namespace** — A mapping from names to objects (a module's globals, a function's locals, an instance's attributes).

**None** — The singleton object representing "no value." The implicit return of a function with no `return`.

## O

*O in Glossary — what it is and when to use it.*

**OOP** — Object-Oriented Programming. Modeling with classes, objects, inheritance, and polymorphism.

**ORM** — Object-Relational Mapper. Maps database rows to objects (SQLAlchemy, Django ORM).

## P

*P in Glossary — what it is and when to use it.*

**Parameter** — A variable named in a function definition. Compare *argument* (the value supplied at call time).

**PEP** — Python Enhancement Proposal. The process and documents for proposing changes to Python (e.g. PEP 8 style).

**Pickle** — Python's native binary serialization format, via the `pickle` module. Never unpickle untrusted data.

**Polymorphism** — Different types responding to the same operation through a shared interface.

**Property** — A managed attribute backed by getter/setter methods, declared with `@property`.

**Protocol** — A typing construct for structural subtyping — duck typing checked by type tools.

## Q

*Q in Glossary — what it is and when to use it.*

**Queue** — A FIFO data structure; `queue.Queue` for threads, `asyncio.Queue` for coroutines, message brokers for services.

## R

*R in Glossary — what it is and when to use it.*

**Race condition** — A bug where the outcome depends on unpredictable timing between concurrent operations.

**Recursion** — A function calling itself, with a base case to stop. Pairs well with memoization.

**Reference counting** — CPython's primary memory scheme: an object is freed when its reference count hits zero.

**REST** — Representational State Transfer. An HTTP API style using resources, verbs, and status codes.

## S

*S in Glossary — what it is and when to use it.*

**Scope** — The region where a name is visible. Python resolves names by the LEGB rule (Local, Enclosing, Global, Built-in).

**Set** — The built-in unordered collection of unique, hashable elements.

**Slicing** — Extracting a subsequence with `seq[start:stop:step]`.

**Slots** — Declaring `__slots__` to store instance attributes compactly and skip the per-instance `__dict__`.

**String** — The immutable text type, `str`, a sequence of Unicode code points.

## T

*T in Glossary — what it is and when to use it.*

**Thread** — An OS-level unit of execution within a process; limited by the GIL for CPU-bound Python code.

**Tuple** — The built-in ordered, immutable sequence type.

**Type hint** — An annotation like `x: int` or `-> str` that documents expected types; checked by tools like `mypy`, not at runtime.

## U

*U in Glossary — what it is and when to use it.*

**Unicode** — The standard that assigns a code point to every character. Python `str` is Unicode; `bytes` is raw bytes.

**Unpacking** — Spreading a sequence or mapping into variables or a call: `a, b = pair`, `f(*args, **kwargs)`.

## V

*V in Glossary — what it is and when to use it.*

**Vectorization** — Replacing explicit Python loops with array-wide operations (NumPy) for speed.

**Virtual environment** — An isolated Python install with its own packages, created by `python -m venv`.

## W

*W in Glossary — what it is and when to use it.*

**Walrus operator** — `:=`, which assigns a value as part of an expression: `if (n := len(xs)) > 10:`.

**Weak reference** — A reference that doesn't keep an object alive, via the `weakref` module.

**WSGI / ASGI** — Standard interfaces between Python web apps and servers. WSGI is synchronous; ASGI supports async.

## Y

*Y in Glossary — what it is and when to use it.*

**Yield** — The keyword that turns a function into a generator; it pauses execution and emits a value. `yield from` delegates to a sub-iterator.

## Z

*Z in Glossary — what it is and when to use it.*

**Zen of Python** — The guiding aphorisms of Python's design, viewable with `import this` (PEP 20).

---

<div class="pm-next">
<strong>✅ Keep going</strong>
<a href="cheatsheets.md">Cheat Sheets</a>
<a href="code-snippets.md">Code Snippets</a>
<a href="tools.md">Tools</a>
</div>
