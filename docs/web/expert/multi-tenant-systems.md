---
title: "Multi-tenant Systems"
description: Serve many customers from one system with data isolation and tenant routing
---

# Multi-tenant Systems <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🌐 Web & APIs Track · Level 6</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="../proficient/databases/">Database Programming</a>, <a href="microservices/">Microservices</a></span>
  </div>
</div>

---

## What you'll learn

- [x] The three data-isolation strategies and their tradeoffs
- [x] Resolve the current tenant from a request
- [x] Carry tenant context safely through a request
- [x] Scope every query so tenants never see each other's data
- [x] The security stakes of getting this wrong

---

## What "multi-tenant" means

A **tenant** is a customer (usually an organization) whose data and users are logically separated from every other customer's — even though they all share the same running application. Slack, Shopify, and Salesforce are multi-tenant: one system, thousands of isolated companies.

The central challenge is **isolation**: tenant A must never, under any circumstances, see tenant B's data. A single missing filter is a data breach.

---

## The three isolation strategies

```
1. Shared DB, shared schema       2. Shared DB, schema-per-tenant   3. Database-per-tenant
   ┌───────────────────┐             ┌───────────────────┐             ┌────┐ ┌────┐ ┌────┐
   │ one table          │             │ schema_acme        │             │ DB │ │ DB │ │ DB │
   │  tenant_id | data  │             │ schema_globex      │             │acme│ │glbx│ │...│
   └───────────────────┘             └───────────────────┘             └────┘ └────┘ └────┘
   every row tagged                   one schema per tenant             fully separate
```

| Strategy | Isolation | Cost / tenant | Scales to many tenants | Blast radius of a bug |
|---|---|---|---|---|
| **Shared schema** (tenant_id column) | Weakest — enforced in code | Lowest | Excellent (thousands) | Highest — one bad query leaks data |
| **Schema per tenant** | Medium | Medium | Good (hundreds) | Medium |
| **Database per tenant** | Strongest — physical | Highest | Limited (tens–low hundreds) | Lowest — DBs can't cross-query |

**How to choose:** shared schema for high-volume SaaS with many small tenants (the common default). Database-per-tenant when tenants are few, large, and demand hard isolation (e.g. enterprise/regulated customers). Schema-per-tenant is the middle ground.

---

## Strategy 1: shared schema, scoped by `tenant_id`

The most common approach — and the most dangerous if done sloppily, because isolation depends entirely on **every query being filtered**. Runnable example:

```python
from contextvars import ContextVar
from dataclasses import dataclass

# The current tenant, set per request. ContextVar keeps it isolated
# across concurrent requests / async tasks (unlike a global variable).
current_tenant: ContextVar[str] = ContextVar("current_tenant")

@dataclass
class Row:
    tenant_id: str
    key: str
    value: str

class SharedStore:
    """One table shared by all tenants; every read is scoped by tenant."""
    def __init__(self) -> None:
        self._rows: list[Row] = []

    def put(self, key: str, value: str) -> None:
        self._rows.append(Row(current_tenant.get(), key, value))

    def all(self) -> list[Row]:
        t = current_tenant.get()
        return [r for r in self._rows if r.tenant_id == t]   # the critical filter
```

Using it — note how tenant context is set and reset around each operation:

```python
store = SharedStore()

token = current_tenant.set("acme")
store.put("plan", "pro")
current_tenant.reset(token)

token = current_tenant.set("globex")
store.put("plan", "free")
current_tenant.reset(token)

# each tenant reads back only their own data
current_tenant.set("acme")
print("acme sees:  ", [(r.key, r.value) for r in store.all()])
current_tenant.set("globex")
print("globex sees:", [(r.key, r.value) for r in store.all()])
```

Output:

```text
acme sees:   [('plan', 'pro')]
globex sees: [('plan', 'free')]
```

Both tenants wrote a `plan` row to the *same* store, yet each reads back only its own. The isolation lives in that one `r.tenant_id == t` line.

!!! danger "The scoping filter must be automatic, never manual"
    Relying on developers to remember `WHERE tenant_id = ?` on every query is how breaches happen — one forgotten filter leaks everyone's data. In production, enforce it structurally: a base query class that always injects the filter, an ORM global filter (e.g. SQLAlchemy events), or PostgreSQL **Row-Level Security** policies that the database enforces regardless of the query. Defense in depth: enforce in the app *and* the database.

### Why `ContextVar`, not a global

A plain global variable would be shared across all concurrent requests — tenant A's request could overwrite tenant B's tenant id mid-flight. `ContextVar` gives each request (and each async task) its own isolated value, so concurrent requests can't clobber each other's tenant.

---

## Tenant routing (resolving who's who)

Before you can scope anything, you must identify the tenant from the incoming request. Common sources:

```python
def resolve_tenant(host: str) -> str:
    """Subdomain routing: acme.example.com -> 'acme'."""
    return host.split(".")[0]

print(resolve_tenant("acme.example.com"))   # -> acme
```

Typical strategies:

- **Subdomain** — `acme.example.com` (clean, common for SaaS).
- **Path prefix** — `example.com/acme/...`.
- **JWT claim / API key** — tenant id embedded in the auth token (best for APIs).
- **Header** — e.g. `X-Tenant-ID` (internal services).

In a web framework this lives in **middleware**: resolve the tenant once per request, set it into the `ContextVar`, and every downstream query is automatically scoped.

```python
# FastAPI-style middleware (illustrative)
async def tenant_middleware(request, call_next):
    tenant = resolve_tenant(request.headers["host"])
    token = current_tenant.set(tenant)
    try:
        return await call_next(request)
    finally:
        current_tenant.reset(token)   # always clean up
```

!!! note "Middleware snippet is illustrative"
    The middleware requires a running framework, so it isn't run-verified here (the store and `resolve_tenant` examples above are). It shows the standard pattern: resolve → set context → process → reset.

---

## Cross-cutting concerns

Multi-tenancy touches more than data reads:

- **Noisy neighbors.** One heavy tenant can starve others of CPU/DB connections. Mitigate with per-tenant rate limits, connection-pool quotas, or moving big tenants to dedicated resources.
- **Per-tenant configuration.** Feature flags, branding, and limits often vary by tenant — store them keyed by tenant id.
- **Migrations.** Shared schema: migrate once. Schema/DB-per-tenant: migrate every tenant, ideally automated and idempotent.
- **Onboarding & offboarding.** Creating a tenant (and cleanly deleting all its data on exit — a real compliance requirement) must be a reliable, tested operation.
- **Backups & data export.** Regulations may require exporting or deleting a single tenant's data; database-per-tenant makes this trivial, shared-schema makes it a careful scoped operation.

---

## Security checklist

Because a mistake here is a cross-customer data leak, treat isolation as a security control:

- [ ] Every data-access path is scoped by tenant — enforced structurally, not by convention.
- [ ] Tenant id comes from a trusted source (auth token), not a user-supplied field they can tamper with.
- [ ] Tests include a "tenant A cannot read tenant B" case for each resource.
- [ ] Consider database-level enforcement (Postgres RLS) as a backstop.
- [ ] Logs and error messages don't leak other tenants' identifiers or data.

---

## Practice exercises

1. Add a `delete_all()` method to `SharedStore` that removes only the current tenant's rows, and test that it doesn't touch the other tenant.
2. Write a test that sets tenant "acme", writes data, then switches to "globex" and asserts `store.all()` is empty for globex.
3. Implement `resolve_tenant` for path-prefix routing (`/acme/dashboard` -> `acme`).
4. Sketch how you'd enforce the tenant filter automatically so a developer *can't* forget it (base repository, ORM hook, or RLS).
5. Explain when you'd choose database-per-tenant over shared schema, with a concrete example customer.
