---
title: Unicode & Text Processing
description: Strings, encoding, bytes, regex, text normalization and real-world text handling
---

# Unicode & Text Processing <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
    <span>📚 Prerequisite: <a href="../beginner/data-structures/">Data Structures</a></span>
  </div>
</div>

---

## str vs bytes — the fundamental distinction

```python
# str — sequence of Unicode code points (text)
text = "Hello, 世界! 🐍"
print(type(text))     # <class 'str'>
print(len(text))      # 11 characters

# bytes — sequence of raw bytes (binary data)
data = b"Hello, ASCII only"
print(type(data))     # <class 'bytes'>
print(len(data))      # 17 bytes

# Encoding: str → bytes
encoded = text.encode("utf-8")
print(type(encoded))  # <class 'bytes'>
print(len(encoded))   # 18 bytes (Chinese chars = 3 bytes each, emoji = 4)
print(encoded)        # b'Hello, \xe4\xb8\x96\xe7\x95\x8c! \xf0\x9f\x90\x8d'

# Decoding: bytes → str
decoded = encoded.decode("utf-8")
print(decoded == text)   # True
```

---

## Encoding schemes

| Encoding | Bytes/char | Coverage | Use case |
|---|---|---|---|
| ASCII | 1 | English only (0-127) | Legacy systems |
| Latin-1 (ISO-8859-1) | 1 | Western European | Old web pages |
| UTF-8 | 1-4 | All Unicode | **Default everywhere** |
| UTF-16 | 2-4 | All Unicode | Windows internals |
| UTF-32 | 4 | All Unicode | Fixed-width processing |

```python
# UTF-8 is variable-width
print("A".encode("utf-8"))      # b'A'       (1 byte)
print("é".encode("utf-8"))      # b'\xc3\xa9' (2 bytes)
print("中".encode("utf-8"))     # b'\xe4\xb8\xad' (3 bytes)
print("🐍".encode("utf-8"))    # b'\xf0\x9f\x90\x8d' (4 bytes)

# Handling encoding errors
text = "Café ☕"
text.encode("ascii", errors="replace")    # b'Caf? ?'
text.encode("ascii", errors="ignore")     # b'Caf '
text.encode("ascii", errors="xmlcharrefreplace")  # b'Caf&#233; &#9749;'
```

---

## Unicode code points and names

```python
# Every character has a code point (integer) and a name
print(ord("A"))          # 65
print(ord("🐍"))        # 128013
print(chr(65))           # A
print(chr(128013))       # 🐍
print(hex(ord("中")))    # 0x4e2d

# Unicode escape sequences
print("\u0041")          # A         (4-digit hex)
print("\U0001F40D")      # 🐍        (8-digit hex for chars > 0xFFFF)
print("\N{SNAKE}")       # 🐍        (by name)

# Get character name
import unicodedata
print(unicodedata.name("🐍"))      # SNAKE
print(unicodedata.name("é"))       # LATIN SMALL LETTER E WITH ACUTE
print(unicodedata.category("A"))   # Lu (Letter, uppercase)
print(unicodedata.category("3"))   # Nd (Number, decimal digit)
print(unicodedata.category("!"))   # Po (Punctuation, other)
```

---

## Text normalization

The same visual character can have different byte representations:

```python
import unicodedata

# "é" can be stored two ways:
composed   = "\u00e9"        # single code point: é
decomposed = "e\u0301"       # e + combining acute accent

print(composed == decomposed)       # False!
print(len(composed))                # 1
print(len(decomposed))              # 2
# But they LOOK identical when printed!

# Normalize to compare
nfc = unicodedata.normalize("NFC", decomposed)    # compose
nfd = unicodedata.normalize("NFD", composed)      # decompose

print(nfc == composed)     # True
print(nfd == decomposed)   # True

# Always normalize before comparing user input!
def safe_compare(a, b):
    return unicodedata.normalize("NFC", a) == unicodedata.normalize("NFC", b)
```

### Normalization forms

| Form | Action | Use case |
|---|---|---|
| NFC | Compose (é = single char) | **Default choice** — most compact |
| NFD | Decompose (é = e + accent) | Text analysis, searching |
| NFKC | Compatibility compose | Search normalization |
| NFKD | Compatibility decompose | Stripping formatting |

```python
# NFKC normalizes visual equivalents
print(unicodedata.normalize("NFKC", "ﬁ"))    # fi (ligature → two chars)
print(unicodedata.normalize("NFKC", "①"))    # 1  (circled → plain)
print(unicodedata.normalize("NFKC", "Ⅳ"))    # IV (Roman numeral → letters)
```

---

## String methods — complete reference

### Searching

```python
s = "Hello, World! Hello, Python!"

s.find("Hello")       # 0  (first occurrence, -1 if not found)
s.rfind("Hello")      # 14 (last occurrence)
s.index("Hello")      # 0  (like find, but raises ValueError)
s.count("Hello")      # 2

s.startswith("Hello")        # True
s.endswith(("!", "?", "."))  # True (accepts tuple)

"Python" in s                # True (membership test)
```

### Transforming

```python
s = "  Hello, World!  "

s.strip()          # "Hello, World!"
s.lstrip()         # "Hello, World!  "
s.rstrip()         # "  Hello, World!"
s.strip(" !")      # "Hello, World"  — strip these chars

"hello".upper()           # "HELLO"
"HELLO".lower()           # "hello"
"hello world".title()     # "Hello World"
"hello world".capitalize()  # "Hello world"
"Hello".swapcase()        # "hELLO"

"hello".center(20, "-")   # "-------hello--------"
"hello".ljust(20)         # "hello               "
"hello".rjust(20)         # "               hello"
"42".zfill(8)             # "00000042"

"hello world".replace("world", "Python")    # "hello Python"
"hello world".replace("l", "L", 1)          # "heLlo world" (max 1 replacement)
```

### Splitting and joining

```python
"a,b,c".split(",")           # ['a', 'b', 'c']
"a  b  c".split()            # ['a', 'b', 'c']  (splits on any whitespace)
"a,b,c,d".split(",", 2)      # ['a', 'b', 'c,d']  (max 2 splits)
"a\nb\nc".splitlines()       # ['a', 'b', 'c']

",".join(["a", "b", "c"])    # "a,b,c"
" ".join(["Hello", "World"]) # "Hello World"
"\n".join(lines)             # join with newlines

# Partition — split into 3 parts
"user@host.com".partition("@")   # ('user', '@', 'host.com')
"no-at-sign".partition("@")      # ('no-at-sign', '', '')
```

### Testing

```python
"123".isdigit()       # True
"abc".isalpha()       # True
"abc123".isalnum()    # True
"   ".isspace()       # True
"Hello".istitle()     # True
"HELLO".isupper()     # True
"hello".islower()     # True
"var_name".isidentifier()   # True
"print".iskeyword()   # False (use keyword.iskeyword())
```

---

## f-strings — advanced formatting

```python
name = "Alice"
score = 95.678
items = [1, 2, 3]

# Basic
f"Hello, {name}!"                  # "Hello, Alice!"

# Expressions
f"2 + 2 = {2 + 2}"                # "2 + 2 = 4"
f"Items: {len(items)}"             # "Items: 3"

# Format specifiers
f"{score:.2f}"                     # "95.68"   (2 decimal places)
f"{1234567:,}"                     # "1,234,567" (thousands separator)
f"{0.75:.1%}"                      # "75.0%"   (percentage)
f"{'hello':>20}"                   # "               hello" (right-align)
f"{'hello':<20}"                   # "hello               " (left-align)
f"{'hello':^20}"                   # "       hello        " (center)
f"{'hello':*^20}"                  # "*******hello********" (fill char)
f"{42:#x}"                         # "0x2a"  (hex with prefix)
f"{42:#b}"                         # "0b101010" (binary)
f"{42:08d}"                        # "00000042" (zero-padded)

# Self-documenting (Python 3.8+)
x = 42
f"{x = }"                          # "x = 42"
f"{x * 2 = }"                     # "x * 2 = 84"

# Multiline
message = (
    f"Name: {name}\n"
    f"Score: {score:.1f}\n"
    f"Grade: {'A' if score >= 90 else 'B'}"
)

# Nested f-strings
width = 20
f"{'hello':^{width}}"             # "       hello        "
```

---

## Real-world text processing patterns

### Slug generation (URL-safe strings)

```python
import re
import unicodedata

def slugify(text):
    """Convert text to URL-safe slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text

print(slugify("Hello, World! Café ☕"))   # "hello-world-caf"
print(slugify("Python 3.13: What's New"))  # "python-313-whats-new"
```

### Detecting encoding

```python
# pip install chardet
import chardet

with open("mystery.txt", "rb") as f:
    raw = f.read()
    detected = chardet.detect(raw)
    print(detected)   # {'encoding': 'utf-8', 'confidence': 0.99, ...}
    text = raw.decode(detected["encoding"])
```

### Stripping accents

```python
import unicodedata

def strip_accents(text):
    nfd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")

print(strip_accents("Café résumé naïve"))   # "Cafe resume naive"
```

---

## Practice Exercises

1. **Write a function** that detects the encoding of a file and converts it to UTF-8.
2. **Build a text normalizer** that lowercases, strips accents, removes punctuation and collapses whitespace.
3. **Write a slug generator** that handles Unicode input (Chinese, Arabic, emojis).
4. **Parse a log file** with regex and extract structured data (timestamp, level, message).
5. **Implement a simple template engine** that replaces `{{variable}}` placeholders with values from a dict.
6. **Count emoji** in a string by checking Unicode categories.
