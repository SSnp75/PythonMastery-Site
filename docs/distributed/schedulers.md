---
title: "Distributed Schedulers"
description: Run background jobs at scale with Celery and RQ — retries, backoff and failure handling
---

# Distributed Schedulers <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🌐 Distributed Systems</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisites: <a href="queues/">Distributed Queues</a>, <a href="../automation/scripting/">Automation & Scripting</a></span>
  </div>
</div>

---

## What you'll learn

- [x] Why offload work to background jobs
- [x] Celery and RQ, and how they differ
- [x] Retry with exponential backoff
- [x] Handle permanent failures (dead-letter)
- [x] Schedule periodic and delayed jobs

---

## Why background jobs

Some work shouldn't happen inside a web request: sending email, generating a report, processing an upload, calling a slow third-party API. Doing it inline makes the user wait and ties up a web worker. Instead, you **enqueue a job** and return immediately; a separate pool of **worker** processes picks it up and runs it.

```
   web request ──enqueue──▶ [ task queue ]  ──▶ worker pool (runs the job)
       │                    (Redis / broker)         │
       └─ returns fast ◀─                            └─ retries, logs, results
```

This is the [distributed queue](queues.md) pattern applied to task execution. The job systems below (Celery, RQ) build on a broker like Redis or RabbitMQ.

---

## Celery vs RQ

The two most common Python task queues:

| | **Celery** | **RQ (Redis Queue)** |
|---|---|---|
| Complexity | Feature-rich, more config | Simple, minimal |
| Broker | RabbitMQ, Redis, others | Redis only |
| Scheduling | Built-in periodic (Celery Beat) | Needs `rq-scheduler` |
| Best for | Large, complex workloads | Straightforward background jobs |

Defining and calling a Celery task:

```python
from celery import Celery   # pip install celery

app = Celery("tasks", broker="redis://localhost:6379/0")

@app.task
def send_email(to: str, subject: str) -> str:
    # ... actually send ...
    return f"sent to {to}"

# enqueue (returns immediately; a worker runs it later)
send_email.delay("user@example.com", "Welcome!")
```

!!! note "Celery/RQ snippets need a broker + running workers"
    These follow the documented APIs and aren't run-verified here (the retry/backoff and dead-letter logic below **is** tested). You'd start workers separately (`celery -A tasks worker`) and they'd consume from Redis.

---

## Retry with exponential backoff

Jobs fail — a network blip, a rate limit, a briefly-down dependency. The right response to a *transient* failure is to retry, but not instantly and not forever. **Exponential backoff** waits progressively longer between attempts (and real systems add random *jitter* to avoid a thundering herd of synchronized retries). Fully runnable:

```python
def backoff_delays(base: float, attempts: int, cap: float) -> list[float]:
    """Delay before each attempt: base * 2^i, capped."""
    return [min(base * (2 ** i), cap) for i in range(attempts)]
```

```python
print(backoff_delays(base=0.5, attempts=6, cap=10.0))
```

Output:

```text
[0.5, 1.0, 2.0, 4.0, 8.0, 10.0]
```

Each retry waits twice as long as the last (0.5s → 1s → 2s → 4s → 8s), then caps at 10s so it never grows unboundedly. This spreads out retries so a struggling downstream service gets breathing room instead of being hammered.

---

## Handling permanent failures: dead-letter

Not every failure is transient. A malformed job or a permanently-broken dependency will fail every retry. After a bounded number of attempts, you must **give up gracefully** and set the job aside (a *dead-letter*) rather than retry forever. Runnable:

```python
def run_task(task, max_retries: int) -> dict:
    last = None
    for attempt in range(max_retries + 1):
        try:
            result = task(attempt)
            return {"status": "done", "attempts": attempt + 1, "result": result}
        except Exception as e:
            last = str(e)
    return {"status": "dead_letter", "attempts": max_retries + 1, "error": last}
```

```python
def flaky(attempt):
    if attempt < 2:
        raise RuntimeError("temporary")   # fails twice, then succeeds
    return "success"

def always_fails(attempt):
    raise RuntimeError("permanent")

print(run_task(flaky, max_retries=3))
print(run_task(always_fails, max_retries=2))
```

Output:

```text
{'status': 'done', 'attempts': 3, 'result': 'success'}
{'status': 'dead_letter', 'attempts': 3, 'error': 'permanent'}
```

The `flaky` job recovers on its third attempt and reports `done`. The `always_fails` job exhausts its retries and is dead-lettered with the error recorded — so it can be inspected later instead of blocking the queue or retrying endlessly. Celery and RQ provide this (`max_retries`, `retry_backoff`, dead-letter routing) so you configure rather than hand-code it, but the logic is exactly this.

!!! tip "Make retried tasks idempotent"
    Since a task may run more than once (a retry after a partial success, or a duplicate delivery), design it to be safe to repeat — the same [idempotency](queues.md) discipline as queue consumers. "Charge the card" should check whether it already charged; "send email" should dedup. Otherwise a retry double-charges.

---

## Scheduling periodic and delayed work

Beyond "run this now in the background," schedulers also handle:

- **Delayed jobs** — "run this in 10 minutes" (send a reminder, expire a session).
- **Periodic jobs** — "every night at 2am, generate the report" (Celery Beat, `rq-scheduler`, or cron feeding the queue).

For simple, single-machine timing, OS cron (see [Automation & Scripting](../automation/scripting.md)) may be enough. For distributed, retried, monitored jobs across many workers, a task queue is the right tool.

---

## Practice exercises

1. Add jitter to `backoff_delays`: return `min(base * 2**i, cap) * random_factor` and explain why jitter prevents synchronized retry storms.
2. Extend `run_task` to only retry on certain exception types (transient) and immediately dead-letter others (permanent) — don't waste retries on a bug.
3. Track and return the list of per-attempt delays alongside the result.
4. Make `flaky` idempotent by having it record a side effect only once even across retries.
5. Decide, for five example jobs (email, nightly report, thumbnail, payment, cleanup), whether you'd use cron or a task queue, and why.
