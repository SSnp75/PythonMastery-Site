---
title: Logging
description: stdlib logging, structlog, loguru, structured logging and log aggregation
---

# Logging <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>📡 Observability Track · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
  </div>
</div>

---

## stdlib logging — the foundation

```python
import logging

# ─── Basic config (quick start) ───────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

logger.debug("Detailed diagnostic info")
logger.info("General operational messages")
logger.warning("Something unexpected but not critical")
logger.error("Something failed")
logger.critical("System is unusable")

# Output:
# 2026-08-23 23:15:30 [DEBUG] __main__: Detailed diagnostic info
# 2026-08-23 23:15:30 [INFO] __main__: General operational messages
# ...
```

### Log levels (in order of severity):

| Level | Value | Use case |
|---|---|---|
| DEBUG | 10 | Diagnostic detail (dev only) |
| INFO | 20 | Normal operation events |
| WARNING | 30 | Something unexpected happened |
| ERROR | 40 | A specific operation failed |
| CRITICAL | 50 | System can't continue |

---

## Production logging configuration

```python
import logging
import logging.handlers
import sys

def setup_logging(level=logging.INFO):
    """Configure logging for production."""
    root = logging.getLogger()
    root.setLevel(level)

    # Console handler (stderr)
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(level)
    console.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    ))
    root.addHandler(console)

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        "app.log",
        maxBytes=10_000_000,    # 10 MB
        backupCount=5,          # keep 5 rotated files
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
    ))
    root.addHandler(file_handler)

    # Suppress noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

setup_logging()
```

---

## Structured logging with structlog

Plain text logs are hard to parse. Structured logs output JSON — perfect for log aggregation.

```python
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),   # human-readable in dev
        # structlog.processors.JSONRenderer(),   # JSON in production
    ],
)

logger = structlog.get_logger()

# ─── Structured fields ────────────────────────────
logger.info("user_login", user_id=42, ip="192.168.1.1", method="oauth2")
# Output (dev):
# 2026-08-23T23:15:30Z [info] user_login  user_id=42 ip=192.168.1.1 method=oauth2

# Output (JSON, production):
# {"event": "user_login", "user_id": 42, "ip": "192.168.1.1", "method": "oauth2", "level": "info", "timestamp": "2026-08-23T23:15:30Z"}

# ─── Binding context ─────────────────────────────
log = logger.bind(request_id="abc-123", user_id=42)
log.info("processing_started")
log.info("step_completed", step="validation")
log.error("processing_failed", error="timeout")
# All messages include request_id and user_id automatically

# ─── Context variables (across function calls) ────
from structlog.contextvars import bind_contextvars, clear_contextvars

def handle_request(request):
    bind_contextvars(request_id=request.id, user=request.user)
    logger.info("request_received", path=request.path)
    process(request)   # all logs inside include request_id
    clear_contextvars()
```

---

## loguru — simpler alternative

```python
from loguru import logger

# Remove default handler and add custom
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - {message}",
    level="INFO",
)
logger.add("app.log", rotation="10 MB", retention="7 days", compression="gz")

# Usage — no getLogger() needed
logger.info("Starting application")
logger.debug("Debug message with {variable}", variable="interpolation")
logger.error("Something failed: {err}", err=exception)

# Exception logging with traceback
@logger.catch   # catches and logs any exception with full traceback
def risky_function():
    return 1 / 0
```

---

## Logging best practices

!!! tip "Rules"
    
    1. **Use structured logging** in production (JSON) — searchable in log aggregation tools
    2. **Include context** — request ID, user ID, trace ID in every log
    3. **Don't log sensitive data** — passwords, tokens, PII
    4. **Use appropriate levels** — don't put everything at INFO
    5. **Log at boundaries** — function entry/exit, external API calls, errors
    6. **Never use print()** in production code — use logging

### What to log:

```python
# Good — actionable, structured
logger.info("order_created", order_id=123, user_id=42, total=99.99, items=3)
logger.error("payment_failed", order_id=123, error="card_declined", retry=True)

# Bad — unstructured, unhelpful
logger.info("Order created")
logger.error(f"Error: {e}")
print("something happened")
```

---

## Practice Exercises

1. **Set up production logging** with rotation, structured format and different levels per handler.
2. **Add request tracing** — bind a request_id to every log message in a web request lifecycle.
3. **Build a log parser** that reads JSON logs and generates summary statistics.
4. **Configure log aggregation** — send logs to a central service (ELK, Loki, CloudWatch).
5. **Implement audit logging** — track who did what, when, from where (separate from operational logs).
6. **Compare** stdlib logging vs structlog vs loguru — performance and developer experience.
