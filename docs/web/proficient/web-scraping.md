---
title: Web Scraping
description: BeautifulSoup, Scrapy, Playwright, handling pagination, proxies and ethical scraping
---

# Web Scraping <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🌐 Web & APIs Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisite: <a href="apis-http/">APIs & HTTP</a></span>
  </div>
</div>

---

## BeautifulSoup — parsing static HTML

```python
import httpx
from bs4 import BeautifulSoup

# Fetch and parse
html = httpx.get("https://news.ycombinator.com").text
soup = BeautifulSoup(html, "html.parser")

# ─── Finding elements ─────────────────────────────
# By tag
titles = soup.find_all("span", class_="titleline")
for t in titles[:5]:
    link = t.find("a")
    print(f"{link.text} → {link['href']}")

# By CSS selector (most flexible)
items = soup.select("tr.athing .titleline > a")
for item in items[:5]:
    print(item.text, item["href"])

# By ID
header = soup.find(id="hnmain")

# By attribute
links = soup.find_all("a", attrs={"rel": "nofollow"})

# Get text content
page_text = soup.get_text(separator="\n", strip=True)
```

### Navigating the tree

```python
# Parent, siblings, children
element = soup.find("span", class_="score")
row = element.parent                  # go up
next_row = element.find_next_sibling("tr")   # next sibling
children = list(element.children)      # direct children
descendants = list(element.descendants)  # all nested elements

# CSS selectors — powerful patterns
soup.select("div.content > p")           # direct child
soup.select("div.content p")             # any descendant
soup.select("a[href^='https']")          # attribute starts with
soup.select("a[href$='.pdf']")           # attribute ends with
soup.select("a[href*='python']")         # attribute contains
soup.select("li:nth-child(2)")           # second <li>
soup.select("p.intro, p.summary")       # multiple selectors
```

### Extracting structured data

```python
def scrape_product(url: str) -> dict:
    html = httpx.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    return {
        "title": soup.select_one("h1.product-title").text.strip(),
        "price": float(soup.select_one(".price").text.strip("$")),
        "rating": float(soup.select_one(".rating")["data-value"]),
        "description": soup.select_one(".description").text.strip(),
        "images": [img["src"] for img in soup.select(".gallery img")],
        "in_stock": "In Stock" in soup.select_one(".availability").text,
    }
```

---

## Handling pagination

```python
import httpx
from bs4 import BeautifulSoup

def scrape_all_pages(base_url: str) -> list[dict]:
    all_items = []
    page = 1

    while True:
        print(f"  Scraping page {page}...")
        response = httpx.get(f"{base_url}?page={page}")

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select(".item")

        if not items:   # no more items = last page
            break

        for item in items:
            all_items.append({
                "name": item.select_one(".name").text.strip(),
                "price": item.select_one(".price").text.strip(),
            })

        # Check for "next" link
        next_link = soup.select_one("a.next-page")
        if not next_link:
            break

        page += 1
        import time
        time.sleep(1)   # be respectful!

    return all_items
```

---

## Playwright — JavaScript-rendered pages

```python
from playwright.sync_api import sync_playwright

def scrape_dynamic_page(url: str) -> list[dict]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url)
        page.wait_for_selector(".product-card")   # wait for JS to render

        # Scroll to load more (infinite scroll)
        for _ in range(5):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)

        # Extract after all content loaded
        cards = page.query_selector_all(".product-card")
        results = []
        for card in cards:
            results.append({
                "name": card.query_selector(".title").inner_text(),
                "price": card.query_selector(".price").inner_text(),
            })

        browser.close()
        return results
```

### Async Playwright

```python
import asyncio
from playwright.async_api import async_playwright

async def scrape_multiple(urls: list[str]) -> list[dict]:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        results = []

        for url in urls:
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_load_state("networkidle")

            title = await page.title()
            content = await page.content()
            results.append({"url": url, "title": title, "html_length": len(content)})

            await page.close()

        await browser.close()
        return results
```

---

## Scrapy — production-grade scraping framework

```python
# items.py
import scrapy

class ProductItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()

# spiders/products.py
import scrapy
from ..items import ProductItem

class ProductSpider(scrapy.Spider):
    name = "products"
    start_urls = ["https://example.com/products"]
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS": 4,
    }

    def parse(self, response):
        for product in response.css(".product-card"):
            item = ProductItem()
            item["name"] = product.css("h3::text").get()
            item["price"] = product.css(".price::text").get()
            item["url"] = response.urljoin(product.css("a::attr(href)").get())
            yield item

        # Follow pagination
        next_page = response.css("a.next-page::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)
```

```bash
# Run spider
scrapy crawl products -o products.json
scrapy crawl products -o products.csv
```

---

## Anti-scraping countermeasures and solutions

| Countermeasure | Solution |
|---|---|
| Rate limiting | Add delays (`time.sleep`), respect `Crawl-delay` |
| User-Agent blocking | Rotate User-Agent strings |
| IP blocking | Use proxy rotation |
| CAPTCHAs | Use CAPTCHA solving services or avoid triggering |
| Dynamic content (JS) | Use Playwright/Selenium |
| Login required | Session cookies, auth flow |
| robots.txt blocking | **Respect it** (ethical obligation) |

### Rotating headers and proxies

```python
import random
import httpx

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
]

PROXIES = [
    "http://proxy1:8080",
    "http://proxy2:8080",
    "http://proxy3:8080",
]

def make_request(url: str) -> httpx.Response:
    return httpx.get(
        url,
        headers={"User-Agent": random.choice(USER_AGENTS)},
        proxy=random.choice(PROXIES),
        timeout=10.0,
    )
```

---

## Ethics and legality

!!! warning "Be a responsible scraper"

    **Always:**
    
    - Check `robots.txt` (`https://site.com/robots.txt`)
    - Add delays between requests (1-3 seconds minimum)
    - Identify yourself with a descriptive User-Agent
    - Cache responses to avoid re-fetching
    - Stop if you get 429 (Too Many Requests)
    
    **Never:**
    
    - Overload a server with rapid requests
    - Scrape behind authentication without permission
    - Redistribute copyrighted content
    - Ignore terms of service

```python
import httpx

def check_robots(base_url: str, path: str) -> bool:
    """Check if a path is allowed by robots.txt."""
    from urllib.robotparser import RobotFileParser
    rp = RobotFileParser()
    rp.set_url(f"{base_url}/robots.txt")
    rp.read()
    return rp.can_fetch("*", f"{base_url}{path}")
```

---

## Data cleaning and storage

```python
import json
import csv
import re

def clean_price(raw: str) -> float:
    """Extract numeric price from messy string."""
    cleaned = re.sub(r"[^\d.]", "", raw)
    return float(cleaned) if cleaned else 0.0

def clean_text(raw: str) -> str:
    """Normalize whitespace and strip."""
    return re.sub(r"\s+", " ", raw).strip()

# Save to JSON
def save_json(data: list[dict], path: str):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Save to CSV
def save_csv(data: list[dict], path: str):
    if not data:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
```

---

## Practice Exercises

1. **Scrape HackerNews** — get top 30 stories with title, URL, score and comment count.
2. **Build a price tracker** that scrapes a product page daily and alerts on price drops.
3. **Scrape a JavaScript-heavy site** (e.g., an SPA) using Playwright.
4. **Handle infinite scroll** — scrape all items from a page that loads content on scroll.
5. **Build a Scrapy spider** with proper pagination, error handling and CSV export.
6. **Write a respectful scraper** that checks robots.txt, rotates User-Agents and handles rate limits.
