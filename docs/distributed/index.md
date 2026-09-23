---
title: "Distributed Systems"
description: Theory and practice of distributed Python systems — consensus, consistency, caching, queues and observability
---

# 🌐 Distributed Systems

**Many machines working as one — and the theory, tradeoffs, and tools that make that reliable.**

A distributed system spreads work and data across multiple machines connected by an unreliable network. That unlocks scale and resilience, but introduces problems a single machine never has: partial failures, network partitions, clock skew, and the impossibility of everyone agreeing instantly. This section covers the foundational theory and the practical Python tools for building such systems.

---

## The fallacies and the fundamental tradeoff

New distributed systems are often built on false assumptions — the classic **fallacies of distributed computing**: that the network is reliable, latency is zero, bandwidth is infinite, and the topology never changes. None hold. Designing well means assuming the network *will* drop messages, delay them, and partition.

The tradeoff this forces is captured by the **CAP theorem**:

> When a network **partition** (P) happens, a distributed system can preserve **consistency** (C) *or* **availability** (A) — not both.

```
   During a partition, you must choose:

   Consistency (CP)              Availability (AP)
   reject writes rather than     accept writes on both sides,
   risk disagreement             reconcile conflicts later
   (e.g. etcd, Spanner)          (e.g. Dynamo, Cassandra)
```

- **CP systems** stay consistent by refusing operations they can't safely complete during a partition (they sacrifice availability). Consensus systems like [Raft](raft.md) and [Paxos](paxos.md) are here.
- **AP systems** stay available by accepting writes everywhere and reconciling afterward (they sacrifice immediate consistency). This is where [CRDTs](crdts.md) and [multi-region](multi-region-consistency.md) conflict resolution live.

There's no universally "right" choice — you pick per data type based on what the business can tolerate (a payment needs CP; a "like" count is fine AP). Nearly every topic in this section is a response to CAP in some form.

---

## Topics

<ul class="pm-subtopics" markdown="1">
- [🗳️ Raft](raft.md) — understandable consensus: leader election, log replication, majorities
- [🏛️ Paxos](paxos.md) — the classic consensus family and why quorum overlap is safe
- [🔀 CRDTs](crdts.md) — data types that merge without coordination
- [🌍 Multi-region Consistency](multi-region-consistency.md) — geo-replication, conflict resolution, causality
- [⚡ Distributed Caching](caching.md) — consistent hashing, cache-aside, stampede protection
- [📨 Distributed Queues](queues.md) — RabbitMQ/Kafka, delivery guarantees, idempotency
- [⏰ Distributed Schedulers](schedulers.md) — Celery/RQ background jobs, retries, backoff
- [📚 Event Sourcing & CQRS](event-sourcing-cqrs.md) — state as an event log, read/write separation
- [🔍 Distributed Tracing](tracing.md) — follow a request across services with spans
- [↩️ Saga Pattern & Distributed Transactions](saga.md) — cross-service transactions with compensation
- [🧭 Service Discovery](service-discovery.md) — how services find each other, registries and health checks
</ul>

---

## How the topics fit together

```
   AGREEMENT          →  Raft, Paxos              (agree despite failures — CP)
   NO-COORDINATION    →  CRDTs, Multi-region      (converge without agreeing — AP)
   MOVING DATA        →  Queues, Caching          (decouple, buffer, scale reads)
   RUNNING WORK       →  Schedulers               (background jobs, retries)
   RECORDING STATE    →  Event Sourcing & CQRS    (the log is the truth)
   CROSS-SVC CHANGES  →  Saga Pattern             (transactions with compensation)
   FINDING SERVICES   →  Service Discovery        (registry, health, load balance)
   SEEING THE SYSTEM  →  Distributed Tracing      (observe across services)
```

**A suggested path:** start with **consensus** (Raft, then Paxos) to understand how machines agree at all. Then **CRDTs** and **Multi-region Consistency** for the availability-first alternative. **Queues** and **Caching** are the everyday building blocks you'll use most. **Schedulers** and **Event Sourcing** build on queues and events. Finish with **Distributed Tracing** — the tool that makes all of the above debuggable in production.

!!! tip "Use battle-tested implementations"
    A recurring theme: consensus and exactly-once delivery are subtle enough that you should *use* proven systems (etcd, Kafka, Celery) rather than implement them yourself. The value in learning the internals is choosing the right tool and reasoning about its guarantees — which is exactly what these pages aim to give you.
