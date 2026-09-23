---
title: "Intermediate Projects"
description: Real applications — web apps, APIs, dashboards and automation suites
---

# Intermediate Projects <span class="pm-badge pm-badge-proficient">Level 3-4</span>

<div class="pm-topic-header">
  <strong>🛠️ Projects</strong>
  <div class="pm-topic-meta">
    <span>⏱️ Days to weeks each</span>
    <span>📚 Prereqs: <a href="../core/competent/oop-fundamentals.md">OOP</a>, <a href="../web/proficient/frameworks.md">Web Frameworks</a>, <a href="../web/proficient/databases.md">Databases</a></span>
  </div>
</div>

---

These projects combine OOP, web frameworks, databases, and APIs — the skills that make you employable. Each is a realistic application, not a toy.

---

## 1. URL shortener (web app + API)

**Goal:** take a long URL, return a short code; visiting the short code redirects.

- **Skills:** a web framework (FastAPI/Flask), a database, routing, redirects, hashing.
- **Minimal version:** POST a URL → get a code; GET the code → redirect.
- **Stretch:** click analytics, custom aliases, expiry, a small frontend. Ties into [APIs & HTTP](../web/proficient/apis-http.md) and [Database Programming](../web/proficient/databases.md).

## 2. REST API for a resource (e.g. a blog or library)

**Goal:** full CRUD API with a database behind it.

- **Skills:** FastAPI, an ORM (SQLAlchemy), Pydantic schemas, pagination, validation.
- **Minimal version:** create/read/update/delete one resource type.
- **Stretch:** authentication (JWT — see the Auth section), filtering, pagination, automatic docs, tests. This is the archetypal backend project.

## 3. Data dashboard

**Goal:** load a dataset and present interactive charts in a web page.

- **Skills:** Pandas for data, a charting library, a web layer (Streamlit is the fast path, or FastAPI + a frontend).
- **Minimal version:** load a CSV, show one chart.
- **Stretch:** filters, multiple views, live data, deploy it. Uses the Data & AI section (Pandas, visualization).

## 4. Web scraper + pipeline

**Goal:** scrape data from a site, clean it, store it, and report on it.

- **Skills:** `requests`/BeautifulSoup (or Playwright for JS sites — see [Browser Automation](../automation/browser.md)), data cleaning, storage.
- **Minimal version:** scrape one page, save to CSV.
- **Stretch:** paginate, schedule it, store in a database, dedupe. **Scrape ethically** — respect robots.txt and rate limits (see the Browser Automation page).

## 5. Personal finance / expense tracker

**Goal:** record transactions, categorize them, and report spending.

- **Skills:** database, OOP modeling, dates, aggregation, maybe a web UI.
- **Minimal version:** add transactions, show totals by category.
- **Stretch:** budgets, charts, CSV import from a bank export, monthly reports.

## 6. Automation suite

**Goal:** a set of scripts that automate a real chore (backups, report generation, file processing) on a schedule.

- **Skills:** `pathlib`, `subprocess`, scheduling, logging, `argparse`.
- **Minimal version:** one scheduled script that does something useful and logs it.
- **Stretch:** several tasks, config-driven, error notifications. Builds directly on [Automation & Scripting](../automation/scripting.md).

---

## What makes these "intermediate"

Unlike beginner projects, these require you to **integrate** multiple concepts and make **design decisions**: how to structure the code, model the data, handle errors, and test. That integration is the real skill.

!!! tip "Structure and test them"
    Use a proper project layout ([Templates](../reference/templates.md)), write tests (Testing section), and put it on GitHub with a clear README. An intermediate project with tests and docs is portfolio material.

Next: [Advanced Projects](advanced.md) — async, distributed, and production-scale builds.
