---
title: pytest
description: Fixtures, parametrize, markers, plugins, conftest and test organization
---

# pytest <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🧪 Testing Track · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="../core/beginner/functions/">Functions</a></span>
  </div>
</div>

---

## Why pytest?

- Minimal boilerplate — just use `assert`
- Powerful fixtures for setup/teardown
- Rich plugin ecosystem (1000+ plugins)
- Parametrize — run same test with different inputs
- Clear failure messages with diffs
- Industry standard for Python testing

---

## Your first test

```python
# math_utils.py
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

```python
# test_math_utils.py
import pytest
from math_utils import add, divide

def test_add_integers():
    assert add(2, 3) == 5

def test_add_floats():
    assert add(1.5, 2.5) == 4.0

def test_add_strings():
    assert add("hello ", "world") == "hello world"

def test_divide_normal():
    assert divide(10, 2) == 5.0

def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
```

```bash
# Run tests
pytest                          # discover and run all
pytest test_math_utils.py       # specific file
pytest test_math_utils.py::test_add_integers  # specific test
pytest -v                       # verbose output
pytest -x                       # stop on first failure
pytest --tb=short               # shorter tracebacks
```

Output:
```
========================= test session starts ==========================
collected 5 items

test_math_utils.py .....                                         [100%]

========================= 5 passed in 0.02s ============================
```

---

## Assertions — pytest magic

pytest rewrites `assert` statements to show detailed failure info:

```python
def test_list_equality():
    result = [1, 2, 3, 4, 5]
    expected = [1, 2, 3, 4, 6]
    assert result == expected
```

Failure output:
```
    assert result == expected
E   AssertionError: assert [1, 2, 3, 4, 5] == [1, 2, 3, 4, 6]
E     At index 4 diff: 5 != 6
```

### Common assertions:

```python
# Equality
assert result == expected
assert result != other

# Truthiness
assert is_valid
assert not is_empty

# Containment
assert "error" in message
assert item in collection
assert key not in dictionary

# Approximate (for floats)
assert result == pytest.approx(3.14159, rel=1e-5)
assert result == pytest.approx(0.1 + 0.2, abs=1e-10)

# Type
assert isinstance(result, dict)

# None
assert result is None
assert result is not None

# Length
assert len(items) == 5
```

---

## Fixtures — setup and teardown

```python
import pytest
import sqlite3

@pytest.fixture
def db_connection():
    """Create a test database, yield connection, cleanup after."""
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO users (name) VALUES ('Alice')")
    conn.execute("INSERT INTO users (name) VALUES ('Bob')")
    conn.commit()
    yield conn          # test runs here
    conn.close()        # cleanup after test

def test_count_users(db_connection):
    cursor = db_connection.execute("SELECT COUNT(*) FROM users")
    assert cursor.fetchone()[0] == 2

def test_find_alice(db_connection):
    cursor = db_connection.execute("SELECT name FROM users WHERE name = ?", ("Alice",))
    assert cursor.fetchone()[0] == "Alice"
```

### Fixture scopes:

```python
@pytest.fixture(scope="function")   # default — fresh per test
def per_test(): ...

@pytest.fixture(scope="class")      # shared across test class
def per_class(): ...

@pytest.fixture(scope="module")     # shared across entire file
def per_module(): ...

@pytest.fixture(scope="session")    # shared across entire test run
def per_session(): ...
```

### Fixture dependencies (fixtures using fixtures):

```python
@pytest.fixture
def app():
    """Create Flask test app."""
    app = create_app(testing=True)
    return app

@pytest.fixture
def client(app):
    """Create test client from app."""
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """Logged-in client."""
    client.post("/login", json={"user": "admin", "pass": "secret"})
    return client

def test_protected_route(auth_client):
    response = auth_client.get("/dashboard")
    assert response.status_code == 200
```

---

## conftest.py — shared fixtures

Place fixtures in `conftest.py` — automatically available to all tests in that directory:

```
tests/
├── conftest.py          ← fixtures shared by ALL tests
├── test_users.py
├── test_orders.py
└── api/
    ├── conftest.py      ← fixtures only for api/ tests
    └── test_endpoints.py
```

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_user():
    return {"name": "Alice", "email": "alice@example.com", "age": 30}

@pytest.fixture(autouse=True)   # runs for EVERY test automatically
def reset_database(db):
    yield
    db.rollback()   # undo any changes after each test
```

---

## Parametrize — multiple inputs, one test

```python
import pytest

@pytest.mark.parametrize("input_val, expected", [
    (1, 1),
    (2, 4),
    (3, 9),
    (4, 16),
    (0, 0),
    (-3, 9),
])
def test_square(input_val, expected):
    assert input_val ** 2 == expected


# Multiple parameters
@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add(a, b, expected):
    assert add(a, b) == expected


# Parametrize with IDs (for readable output)
@pytest.mark.parametrize("email, valid", [
    ("user@example.com", True),
    ("invalid", False),
    ("@no-local.com", False),
    ("user@.com", False),
    ("a@b.co", True),
], ids=["valid_email", "no_at", "no_local", "no_domain", "short_valid"])
def test_email_validation(email, valid):
    assert is_valid_email(email) == valid
```

Output:
```
test_validation.py::test_email_validation[valid_email] PASSED
test_validation.py::test_email_validation[no_at] PASSED
test_validation.py::test_email_validation[no_local] PASSED
test_validation.py::test_email_validation[no_domain] PASSED
test_validation.py::test_email_validation[short_valid] PASSED
```

---

## Markers — categorize and filter tests

```python
import pytest

@pytest.mark.slow
def test_large_dataset():
    """Takes 30+ seconds."""
    process_million_records()

@pytest.mark.integration
def test_external_api():
    """Requires network."""
    response = call_external_service()
    assert response.ok

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.platform == "win32", reason="Linux only")
def test_unix_signals():
    pass

@pytest.mark.xfail(reason="Known bug #123")
def test_known_broken():
    assert broken_function() == expected   # won't cause test suite failure
```

```bash
# Run only fast tests (exclude slow)
pytest -m "not slow"

# Run only integration tests
pytest -m integration

# Run everything except integration
pytest -m "not integration"
```

Register custom markers in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow (deselect with '-m not slow')",
    "integration: marks integration tests",
]
```

---

## Testing exceptions

```python
import pytest

def test_raises_value_error():
    with pytest.raises(ValueError):
        int("not a number")

def test_raises_with_message():
    with pytest.raises(ValueError, match=r"invalid literal for int\(\)"):
        int("abc")

def test_raises_and_inspect():
    with pytest.raises(ValueError) as exc_info:
        divide(1, 0)
    assert "zero" in str(exc_info.value)
    assert exc_info.type == ValueError
```

---

## Testing output (capsys)

```python
def greet(name):
    print(f"Hello, {name}!")

def test_greet_output(capsys):
    greet("Alice")
    captured = capsys.readouterr()
    assert captured.out == "Hello, Alice!\n"
    assert captured.err == ""
```

---

## Temporary files and directories (tmp_path)

```python
def test_write_and_read(tmp_path):
    # tmp_path is a pathlib.Path to a unique temporary directory
    file = tmp_path / "data.txt"
    file.write_text("hello world")

    assert file.read_text() == "hello world"
    assert file.exists()
    # tmp_path is cleaned up automatically after test
```

---

## Async tests

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    result = await fetch_data("https://api.example.com")
    assert result["status"] == "ok"

@pytest.fixture
async def async_client():
    async with httpx.AsyncClient() as client:
        yield client

@pytest.mark.asyncio
async def test_api_call(async_client):
    response = await async_client.get("https://httpbin.org/get")
    assert response.status_code == 200
```

Requires: `pip install pytest-asyncio`

---

## Test organization best practices

```
project/
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── models.py
│       ├── services.py
│       └── utils.py
├── tests/
│   ├── conftest.py          # shared fixtures
│   ├── unit/                # fast, isolated
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_utils.py
│   ├── integration/         # database, external services
│   │   ├── test_db.py
│   │   └── test_api.py
│   └── e2e/                 # full system tests
│       └── test_workflows.py
└── pyproject.toml
```

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "slow",
    "integration",
    "e2e",
]
```

---

## Useful plugins

| Plugin | Purpose |
|---|---|
| `pytest-cov` | Coverage reporting |
| `pytest-asyncio` | Async test support |
| `pytest-mock` | Simplified mocking |
| `pytest-xdist` | Parallel test execution |
| `pytest-randomly` | Randomize test order |
| `pytest-timeout` | Fail tests that hang |
| `pytest-benchmark` | Performance benchmarks |
| `pytest-freezegun` | Mock time/dates |

```bash
# Run tests in parallel (4 workers)
pytest -n 4

# With coverage
pytest --cov=src --cov-report=html

# Random order (find hidden dependencies)
pytest -p randomly
```

---

## Practice Exercises

1. **Write tests for a calculator** — cover add, subtract, multiply, divide including edge cases (zero, negatives, floats).
2. **Use parametrize** to test a password validator with 20+ test cases.
3. **Write fixture chains** — `db_connection` → `populated_db` → `user_service` → test.
4. **Test a REST API** using `pytest` + `httpx` with setup/teardown fixtures.
5. **Organize tests** into unit/integration/e2e directories with appropriate markers.
6. **Use `pytest-xdist`** to run a large test suite in parallel and measure speedup.
