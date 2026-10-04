---
title: Dates & Times
description: datetime, date, timedelta, formatting, parsing and timezone-aware datetimes with zoneinfo
---

# Dates & Times <span class="pm-badge pm-badge-competent">Competent</span>

<div class="pm-topic-header">
  <strong>🐍 Core Python Track · Level 2</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~2 days</span>
    <span>📚 Prerequisite: <a href="standard-library/">Standard Library</a></span>
  </div>
</div>

---

The `datetime` module handles dates and times; `zoneinfo` (3.9+) adds real timezone support
from the system's IANA database.

---

## Building dates and times

*Building dates and times in Dates & Times — what it is and when to use it.*

```python
from datetime import date, datetime, time

d = date(2026, 1, 15)
print(d.year, d.month, d.day)   # 2026 1 15
print(d.weekday())              # 3  (Mon=0 ... Thu=3)

dt = datetime(2026, 1, 15, 9, 30, 0)
print(dt.hour, dt.minute)       # 9 30
```

---

## Formatting (`strftime`) and parsing (`strptime`)

*Formatting (strftime) and parsing (strptime) in Dates & Times — what it is and when to use it.*

```python
from datetime import datetime

dt = datetime(2026, 1, 15, 9, 5)
print(dt.strftime("%Y-%m-%d %H:%M"))        # 2026-01-15 09:05
print(dt.strftime("%A, %B %d"))             # Thursday, January 15

parsed = datetime.strptime("2026-01-15", "%Y-%m-%d")
print(parsed.date())                        # 2026-01-15
```

Common codes: `%Y` year, `%m` month, `%d` day, `%H` hour, `%M` minute, `%S` second,
`%A` weekday name, `%B` month name.

---

## ISO format (preferred for storage/exchange)

*ISO format (preferred for storage/exchange) in Dates & Times — what it is and when to use it.*

```python
from datetime import datetime

dt = datetime(2026, 1, 15, 9, 5, 0)
print(dt.isoformat())                       # 2026-01-15T09:05:00
print(datetime.fromisoformat("2026-01-15T09:05:00").hour)   # 9
```

---

## Arithmetic with `timedelta`

*Arithmetic with timedelta in Dates & Times — what it is and when to use it.*

```python
from datetime import datetime, timedelta

dt = datetime(2026, 1, 15, 12, 0)
print((dt + timedelta(days=7)).date())      # 2026-01-22
print((dt - timedelta(hours=3)).hour)       # 9

delta = datetime(2026, 1, 20) - datetime(2026, 1, 15)
print(delta.days)                           # 5
print(delta.total_seconds())                # 432000.0
```

---

## Timezone-aware datetimes with `zoneinfo`

*Timezone-aware datetimes with zoneinfo in Dates & Times — what it is and when to use it.*

Naive datetimes have no timezone; aware ones carry a `tzinfo`. Prefer aware for anything
real-world.

```python
from datetime import datetime
from zoneinfo import ZoneInfo

utc = datetime(2026, 1, 15, 12, 0, tzinfo=ZoneInfo("UTC"))
ny = utc.astimezone(ZoneInfo("America/New_York"))
print(ny.hour)                 # 7  (UTC-5 in January)
print(utc.tzinfo)              # UTC
print(ny.utcoffset().total_seconds() / 3600)   # -5.0
```

---

## Unix timestamps

*Unix timestamps in Dates & Times — what it is and when to use it.*

```python
from datetime import datetime, timezone

dt = datetime(2026, 1, 15, tzinfo=timezone.utc)
ts = dt.timestamp()
print(datetime.fromtimestamp(ts, tz=timezone.utc).year)   # 2026
```

!!! warning "Naive vs aware"
    You cannot subtract an aware datetime from a naive one — it raises `TypeError`. Pick one
    convention (ideally UTC-aware) and convert at the edges of your system.

---

## Practice exercises

1. Compute how many days until a given future date.
2. Parse `"15/01/2026 09:30"` with the right `strptime` format.
3. Convert a UTC datetime to three different timezones with `zoneinfo`.
4. Given two ISO datetime strings, print the duration between them in hours.
