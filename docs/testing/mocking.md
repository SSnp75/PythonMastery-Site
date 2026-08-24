---
title: Mocking & Patching
description: unittest.mock, MagicMock, patch, side_effect and testing in isolation
---

# Mocking & Patching <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🧪 Testing Track · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisite: <a href="pytest/">pytest</a></span>
  </div>
</div>

---

## Why mock?

Mocks replace real objects with controlled fakes so you can:

- Test code without hitting databases, APIs or filesystems
- Control the behavior of dependencies (return specific values, raise errors)
- Verify that code called the right functions with the right arguments
- Run tests fast (no network, no I/O)

---

## The Mock object

```python
from unittest.mock import Mock, MagicMock

# Basic Mock
mock = Mock()
mock.some_method(42, "hello")           # doesn't error — any call works
mock.some_method.assert_called_once()   # ✓
mock.some_method.assert_called_with(42, "hello")  # ✓

# Configure return values
mock.get_user.return_value = {"name": "Alice", "age": 30}
result = mock.get_user(user_id=1)
print(result)   # {'name': 'Alice', 'age': 30}

# Chained attribute access
mock.db.session.query.return_value.filter.return_value.first.return_value = "Alice"
result = mock.db.session.query().filter().first()
print(result)   # "Alice"
```

---

## MagicMock — Mock with magic methods

```python
from unittest.mock import MagicMock

# MagicMock supports __len__, __iter__, __getitem__, etc.
mock_list = MagicMock()
mock_list.__len__.return_value = 5
mock_list.__getitem__.return_value = "item"

print(len(mock_list))    # 5
print(mock_list[0])      # "item"

# Iteration
mock_iter = MagicMock()
mock_iter.__iter__.return_value = iter([1, 2, 3])
for item in mock_iter:
    print(item)   # 1, 2, 3

# Context manager
mock_file = MagicMock()
mock_file.__enter__.return_value = mock_file
mock_file.read.return_value = "file contents"

with mock_file as f:
    data = f.read()
print(data)   # "file contents"
```

---

## patch() — replace objects during tests

```python
from unittest.mock import patch, MagicMock
import pytest

# ─── The code under test ──────────────────────────
# services.py
import requests

def get_user_name(user_id):
    """Fetches user from external API."""
    response = requests.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()
    return response.json()["name"]

# ─── The test ─────────────────────────────────────
# test_services.py
from services import get_user_name

@patch("services.requests.get")   # patch WHERE IT'S USED, not where it's defined
def test_get_user_name(mock_get):
    # Configure the mock
    mock_response = MagicMock()
    mock_response.json.return_value = {"name": "Alice", "id": 1}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Call the real function — but requests.get is mocked
    result = get_user_name(1)

    # Assertions
    assert result == "Alice"
    mock_get.assert_called_once_with("https://api.example.com/users/1")
    mock_response.raise_for_status.assert_called_once()
```

### patch as context manager:

```python
def test_with_context_manager():
    with patch("services.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"name": "Bob"}
        mock_get.return_value.raise_for_status.return_value = None

        result = get_user_name(2)
        assert result == "Bob"
```

### patch as decorator with pytest fixture (recommended):

```python
@pytest.fixture
def mock_api():
    with patch("services.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        yield mock_get, mock_response

def test_user_api(mock_api):
    mock_get, mock_response = mock_api
    mock_response.json.return_value = {"name": "Charlie"}
    result = get_user_name(3)
    assert result == "Charlie"
```

---

## side_effect — dynamic mock behavior

```python
from unittest.mock import Mock, patch

# Return different values on successive calls
mock = Mock()
mock.side_effect = [1, 2, 3]
print(mock())   # 1
print(mock())   # 2
print(mock())   # 3

# Raise an exception
mock.side_effect = ValueError("Something broke")
try:
    mock()
except ValueError as e:
    print(e)   # Something broke

# Custom function
def fake_get(url):
    if "users" in url:
        return MagicMock(json=lambda: {"name": "Alice"})
    elif "posts" in url:
        return MagicMock(json=lambda: [{"title": "Post 1"}])
    raise ValueError(f"Unknown URL: {url}")

with patch("services.requests.get", side_effect=fake_get):
    assert get_user_name(1) == "Alice"
```

---

## Assertions on mock calls

```python
from unittest.mock import Mock, call

mock = Mock()
mock(1, 2, key="value")
mock(3, 4)
mock(5)

# Was it called?
mock.assert_called()                    # ✓ (at least once)
assert mock.call_count == 3             # ✓

# Last call
mock.assert_called_with(5)              # ✓ (checks most recent call)

# Specific call in history
assert mock.call_args_list == [
    call(1, 2, key="value"),
    call(3, 4),
    call(5),
]

# Any order
mock.assert_any_call(3, 4)              # ✓ (was called with these args at some point)

# Never called with specific args
assert call(99) not in mock.call_args_list
```

---

## patch.object — patch a method on a specific object

```python
from unittest.mock import patch

class UserService:
    def get_user(self, user_id):
        # Real database call
        return db.query(User).get(user_id)

    def get_user_name(self, user_id):
        user = self.get_user(user_id)
        return user.name

def test_get_user_name():
    service = UserService()
    fake_user = Mock(name="Alice")

    with patch.object(service, "get_user", return_value=fake_user):
        result = service.get_user_name(1)
        assert result == "Alice"
```

---

## patch.dict — temporarily modify dictionaries

```python
import os
from unittest.mock import patch

@patch.dict(os.environ, {"API_KEY": "test-key-123", "DEBUG": "true"})
def test_with_env_vars():
    assert os.environ["API_KEY"] == "test-key-123"
    assert os.environ["DEBUG"] == "true"

# After test, os.environ is restored to original
```

---

## Mocking async code

```python
from unittest.mock import AsyncMock, patch
import pytest

# Async function to test
async def fetch_data(client, url):
    response = await client.get(url)
    return response.json()

@pytest.mark.asyncio
async def test_fetch_data():
    mock_client = AsyncMock()
    mock_client.get.return_value.json.return_value = {"data": "test"}

    result = await fetch_data(mock_client, "https://api.example.com")
    assert result == {"data": "test"}
    mock_client.get.assert_awaited_once_with("https://api.example.com")
```

---

## When to mock vs when NOT to mock

| Mock | Don't mock |
|---|---|
| External APIs (HTTP calls) | Your own pure functions |
| Database queries | Simple data transformations |
| File system I/O | Value objects and dataclasses |
| Time/dates (`datetime.now`) | Business logic (test it directly!) |
| Random numbers | |
| Email sending | |
| Third-party services | |

!!! warning "Over-mocking"
    If your test is 90% mock setup and 10% assertion, you're testing the mocks — not the code. Prefer integration tests for complex interactions.

---

## Practice Exercises

1. **Mock an HTTP API** — test a function that calls 3 different endpoints.
2. **Use `side_effect`** to simulate a flaky API (fails twice, succeeds on third try).
3. **Mock `datetime.now`** to test time-dependent logic (e.g., "is the store open?").
4. **Mock a database** — test a service layer without a real database connection.
5. **Test error handling** — mock a function that raises different exceptions.
6. **Compare** testing with mocks vs testing with a real in-memory SQLite database — discuss trade-offs.
