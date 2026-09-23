---
title: "Advanced Projects"
description: Production-grade builds — async services, distributed workers and complex pipelines
---

# Advanced Projects <span class="pm-badge pm-badge-expert">Level 5-6</span>

<div class="pm-topic-header">
  <strong>🛠️ Projects</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Weeks each</span>
    <span>📚 Prereqs: <a href="../systems/proficient/asyncio.md">Asyncio</a>, <a href="../distributed/queues.md">Queues</a>, <a href="../web/expert/clean-architecture.md">Clean Architecture</a></span>
  </div>
</div>

---

These projects operate at production scale: concurrency, distribution, and real architecture. They exercise the Expert-level material and produce genuinely impressive portfolio pieces.

---

## 1. Async web service with background jobs

**Goal:** an async API that offloads slow work to background workers.

- **Skills:** async FastAPI, a task queue ([Distributed Schedulers](../distributed/schedulers.md)), a broker (Redis), idempotency.
- **Minimal version:** an endpoint that enqueues a job; a worker that processes it.
- **Stretch:** retries with backoff, dead-letter handling, progress tracking, horizontal scaling. Applies [Asyncio](../systems/proficient/asyncio.md) and the Distributed Systems section directly.

## 2. Distributed worker system

**Goal:** distribute a large workload across multiple worker processes/machines.

- **Skills:** message queues ([Distributed Queues](../distributed/queues.md)), idempotent consumers, coordination, monitoring.
- **Minimal version:** a producer + several workers pulling from one queue.
- **Stretch:** work stealing, backpressure, fault tolerance (workers can die and recover), a dashboard. Real application of the queue + idempotency patterns.

## 3. ETL / data pipeline

**Goal:** Extract from sources, Transform/clean, Load into a warehouse — reliably and repeatably.

- **Skills:** data processing, scheduling (Airflow-style DAGs), idempotency, error handling.
- **Minimal version:** a 3-stage pipeline (fetch → clean → store) run on a schedule.
- **Stretch:** incremental loads, data validation, retries, orchestration, observability. Connects to the Data Engineering section.

## 4. Real-time chat / collaboration backend

**Goal:** many clients exchanging messages in real time.

- **Skills:** WebSockets (Networking section), async, pub/sub, presence, state management.
- **Minimal version:** a WebSocket server broadcasting messages to connected clients.
- **Stretch:** rooms, history, presence, scaling across servers with Redis pub/sub, and conflict-free editing with [CRDTs](../distributed/crdts.md) for collaborative documents.

## 5. Your own mini web framework or ORM

**Goal:** build a small version of the tools you use, to understand them deeply.

- **Skills:** WSGI/ASGI, routing, decorators, descriptors ([Descriptors](../core/advanced/descriptors.md)), metaclasses.
- **Minimal version:** a router that maps URLs to functions and returns responses.
- **Stretch:** middleware, a template layer, or (for an ORM) query building and a descriptor-based model layer. Nothing teaches a tool like reimplementing it.

## 6. Clean-architecture application

**Goal:** a non-trivial app built with proper layering, fully testable without infrastructure.

- **Skills:** [Clean](../web/expert/clean-architecture.md) / [Hexagonal Architecture](../web/expert/hexagonal-architecture.md), dependency injection, ports & adapters.
- **Minimal version:** one use case with a domain layer, a port, and a fake adapter, unit-tested.
- **Stretch:** swap adapters (in-memory ↔ real DB), add real infrastructure, prove the core needs no changes. This is the architecture payoff made concrete.

---

## What separates advanced work

At this level, the code working is table stakes. What matters:

- **Concurrency correctness** — no races, proper async, idempotency.
- **Failure handling** — things *will* fail; the system recovers gracefully.
- **Testability** — architecture that lets you test without spinning up the world.
- **Observability** — you can see what the running system is doing ([Distributed Tracing](../distributed/tracing.md), [System Monitoring](../embedded/system-monitoring.md)).

!!! tip "Operate it, don't just build it"
    An advanced project isn't done when it runs once — it's done when you can deploy it (Deployment section), monitor it, and it survives a worker crash. That operational maturity is what employers and open-source users actually value.

Next: [Systems Projects](systems.md) for lower-level tooling, or [Research Projects](research.md) for the frontier.
