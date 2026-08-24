---
title: LLM APIs
description: OpenAI, Anthropic, local models, structured output, streaming and production patterns
---

# LLM APIs <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🤖 AI Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisite: <a href="../web/proficient/apis-http/">APIs & HTTP</a></span>
  </div>
</div>

---

## OpenAI API

```python
from openai import OpenAI

client = OpenAI(api_key="sk-...")   # or set OPENAI_API_KEY env var

# ─── Basic completion ─────────────────────────────
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful Python tutor."},
        {"role": "user", "content": "Explain decorators in 3 sentences."},
    ],
    temperature=0.7,
    max_tokens=200,
)
print(response.choices[0].message.content)
# Output:
# A decorator is a function that takes another function and extends its
# behavior without modifying it. You apply it with the @ syntax above a
# function definition. It's commonly used for logging, timing, and access control.

print(f"Tokens used: {response.usage.total_tokens}")   # e.g. 87
```

---

## Streaming responses

```python
# Stream for real-time display (like ChatGPT)
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a haiku about Python"}],
    stream=True,
)

full_response = ""
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
        full_response += delta
print()   # newline after streaming complete
```

---

## Structured output (JSON mode)

```python
from pydantic import BaseModel

class MovieReview(BaseModel):
    title: str
    rating: float
    sentiment: str
    summary: str
    keywords: list[str]

response = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Extract structured movie review data."},
        {"role": "user", "content": "The new Dune movie was absolutely stunning. "
         "The visuals were breathtaking and Timothée Chalamet was perfect. 9/10."},
    ],
    response_format=MovieReview,
)

review = response.choices[0].message.parsed
print(review.title)       # Dune: Part Two
print(review.rating)      # 9.0
print(review.sentiment)   # positive
print(review.keywords)    # ['visuals', 'stunning', 'Chalamet']
```

---

## Anthropic (Claude) API

```python
from anthropic import Anthropic

client = Anthropic(api_key="sk-ant-...")

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="You are an expert Python code reviewer.",
    messages=[
        {"role": "user", "content": "Review this code:\n```python\ndef f(x): return x*2\n```"}
    ],
)
print(message.content[0].text)
print(f"Input tokens: {message.usage.input_tokens}")
print(f"Output tokens: {message.usage.output_tokens}")
```

---

## Tool calling / Function calling

```python
import json

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in London?"}],
    tools=tools,
    tool_choice="auto",
)

# Model decides to call the tool
tool_call = response.choices[0].message.tool_calls[0]
print(tool_call.function.name)       # get_weather
print(tool_call.function.arguments)  # {"location": "London", "unit": "celsius"}

# Execute the function
args = json.loads(tool_call.function.arguments)
weather_result = get_weather(**args)   # your real function

# Send result back to model
messages = [
    {"role": "user", "content": "What's the weather in London?"},
    response.choices[0].message,
    {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(weather_result)},
]
final_response = client.chat.completions.create(model="gpt-4o", messages=messages)
print(final_response.choices[0].message.content)
# "The current weather in London is 15°C with partly cloudy skies."
```

---

## Local models with Ollama

```python
import httpx

# Ollama runs locally — no API key needed
response = httpx.post(
    "http://localhost:11434/api/generate",
    json={"model": "llama3", "prompt": "Explain Python decorators", "stream": False},
)
print(response.json()["response"])

# Or use the openai-compatible endpoint
from openai import OpenAI

local_client = OpenAI(base_url="http://localhost:11434/v1", api_key="unused")
response = local_client.chat.completions.create(
    model="llama3",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

---

## Production patterns

### Retry with exponential backoff

```python
import time
from openai import OpenAI, RateLimitError, APIError

def call_with_retry(client, messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model="gpt-4o", messages=messages
            )
        except RateLimitError:
            wait = 2 ** attempt
            print(f"  Rate limited. Waiting {wait}s...")
            time.sleep(wait)
        except APIError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(1)
    raise RuntimeError("Max retries exceeded")
```

### Token counting and cost estimation

```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def estimate_cost(input_tokens: int, output_tokens: int, model: str = "gpt-4o") -> float:
    # Prices as of 2024 (check current pricing)
    prices = {
        "gpt-4o": {"input": 0.005, "output": 0.015},      # per 1K tokens
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    }
    p = prices[model]
    return (input_tokens * p["input"] + output_tokens * p["output"]) / 1000

tokens = count_tokens("Hello, how are you?")
print(f"Tokens: {tokens}")   # ~6
cost = estimate_cost(1000, 500, "gpt-4o")
print(f"Estimated cost: ${cost:.4f}")   # $0.0125
```

### Prompt templating

```python
from string import Template

REVIEW_PROMPT = Template("""
You are a code reviewer. Review the following Python code and provide:
1. A score from 1-10
2. Issues found (list)
3. Suggestions for improvement

Code:
```python
$code
```

Respond in JSON format: {"score": int, "issues": [...], "suggestions": [...]}
""")

def review_code(code: str) -> dict:
    prompt = REVIEW_PROMPT.substitute(code=code)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)
```

---

## Practice Exercises

1. **Build a CLI chatbot** that maintains conversation history and streams responses.
2. **Implement function calling** — build an assistant that can query a database and search the web.
3. **Build a code review tool** that uses structured output to return typed review objects.
4. **Implement token-aware chunking** — split long documents to fit within context limits.
5. **Compare APIs** — call OpenAI, Anthropic and a local model with the same prompt, compare quality and speed.
6. **Build a prompt library** with templates for different tasks (summarization, extraction, code generation).
