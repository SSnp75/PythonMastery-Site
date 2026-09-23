---
title: "Browser Automation"
description: Drive real browsers with Selenium and Playwright for testing and scraping
---

# Browser Automation <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🤖 Automation Track</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prereqs: Automation & Scripting, APIs & HTTP</span>
  </div>
</div>

---

## What you'll learn

- [x] Launch and control a real browser from Python
- [x] Find elements and interact with them (click, type, submit)
- [x] Wait reliably for pages and elements to load
- [x] Run headless for speed and servers
- [x] Choose between Selenium and Playwright
- [x] Scrape JavaScript-rendered pages
- [x] Automate responsibly and legally

Browser automation drives a genuine browser (Chrome, Firefox, WebKit) programmatically. Unlike simple HTTP requests, it executes JavaScript, so it can handle single-page apps, dynamic content, and logins. The two dominant tools are **Selenium** (the long-standing standard) and **Playwright** (the modern, faster option).

!!! warning "These examples need the libraries and a browser"
    Nothing here runs without installing the tool and a browser driver. The code is written against each library's stable, documented API. Install commands are shown per section.

---

## Selenium vs Playwright — which to use

| | **Selenium** | **Playwright** |
|---|---|---|
| Maturity | Very mature, huge ecosystem | Newer, rapidly growing |
| Auto-waiting | Manual (explicit waits) | **Built-in** — waits automatically |
| Setup | Needs matching driver (eased by Selenium Manager) | Bundles its own browsers |
| Speed | Good | Generally faster |
| Browsers | Chrome, Firefox, Edge, Safari | Chromium, Firefox, WebKit |
| Best for | Legacy suites, broad language support | New projects, reliability |

**Recommendation:** for a new project, start with **Playwright** — its automatic waiting eliminates the single biggest source of flaky browser scripts. Use Selenium when you're joining an existing Selenium codebase or need a browser it uniquely supports.

---

## Selenium

```bash
pip install selenium
```

Modern Selenium (4.6+) includes **Selenium Manager**, which downloads the right browser driver for you — no more manual driver juggling.

### First script

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()          # launches Chrome
try:
    driver.get("https://example.com")
    print(driver.title)              # 'Example Domain'

    # Find an element and read its text
    heading = driver.find_element(By.TAG_NAME, "h1")
    print(heading.text)              # 'Example Domain'
finally:
    driver.quit()                    # always close the browser
```

!!! tip "Always `quit()` in a `finally`"
    A crashed script that skips `quit()` leaves an orphaned browser process running. The `try/finally` guarantees cleanup even on error.

### Locating elements

Selenium finds elements by a `By` strategy:

```python
from selenium.webdriver.common.by import By

driver.find_element(By.ID, "login")
driver.find_element(By.NAME, "email")
driver.find_element(By.CLASS_NAME, "btn-primary")
driver.find_element(By.CSS_SELECTOR, "form input[type='password']")
driver.find_element(By.XPATH, "//button[text()='Submit']")

# find_elements (plural) returns a list, empty if none match
links = driver.find_elements(By.TAG_NAME, "a")
```

Prefer **CSS selectors** or **IDs** — they're readable and fast. Reserve XPath for cases CSS can't express (like selecting by visible text).

### Interacting & waiting

The #1 cause of flaky Selenium scripts is acting before the page is ready. Use **explicit waits**, never `time.sleep`.

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, timeout=10)

# Wait until the element is present and clickable, THEN act
button = wait.until(EC.element_to_be_clickable((By.ID, "submit")))
button.click()

# Fill a field
email = driver.find_element(By.NAME, "email")
email.clear()
email.send_keys("user@example.com")
```

### Complete example: log in and read a result

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login_and_get_welcome(url: str, user: str, pw: str) -> str:
    """Log in and return the text of the welcome banner."""
    driver = webdriver.Chrome()
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        driver.find_element(By.NAME, "username").send_keys(user)
        driver.find_element(By.NAME, "password").send_keys(pw)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        banner = wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "welcome"))
        )
        return banner.text
    finally:
        driver.quit()

# login_and_get_welcome("https://site/login", "alice", "secret")
# -> 'Welcome back, Alice!'
```

---

## Playwright

```bash
pip install playwright
playwright install          # downloads Chromium, Firefox, WebKit
```

The `playwright install` step grabs the browsers Playwright manages itself, so there's no separate driver to match.

### First script

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://example.com")

    print(page.title())                 # 'Example Domain'
    print(page.inner_text("h1"))        # 'Example Domain'

    browser.close()
```

The `with sync_playwright()` context manager handles startup and teardown — no manual `quit()` needed.

### Auto-waiting: the killer feature

Playwright **automatically waits** for elements to be visible, enabled, and stable before acting. This one behavior removes most flakiness:

```python
# No explicit wait needed — Playwright waits for the button to be
# actionable, then clicks. It retries until a timeout.
page.click("text=Sign in")
page.fill("input[name='email']", "user@example.com")
page.fill("input[name='password']", "secret")
page.click("button[type='submit']")

# Wait for a specific result to appear
page.wait_for_selector(".dashboard")
```

### Locators (the recommended API)

Locators are re-evaluated each time they're used, so they stay valid as the page changes:

```python
# By role + accessible name (robust, mirrors how users find things)
page.get_by_role("button", name="Submit").click()

# By visible label / text / placeholder
page.get_by_label("Email").fill("user@example.com")
page.get_by_text("Welcome").is_visible()
page.get_by_placeholder("Search").fill("python")

# CSS / text selectors still work
page.locator(".product-card").count()
```

### Complete example: scrape a JS-rendered list

Sites that build their content with JavaScript return an near-empty HTML to a plain `requests.get`. A browser runs the JS, so the data is actually there.

```python
from playwright.sync_api import sync_playwright

def scrape_titles(url: str) -> list[str]:
    """Return the text of every .title element after JS has rendered."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")   # wait for network to settle

        titles = page.locator(".title").all_inner_texts()
        browser.close()
        return titles

# scrape_titles("https://example.com/products")
# -> ['Widget A', 'Widget B', 'Widget C']
```

---

## Headless mode

"Headless" means the browser runs without a visible window — faster, and required on servers with no display.

```python
# Playwright
browser = p.chromium.launch(headless=True)

# Selenium
from selenium.webdriver.chrome.options import Options
opts = Options()
opts.add_argument("--headless=new")
driver = webdriver.Chrome(options=opts)
```

Develop with `headless=False` so you can *watch* what happens, then flip to `True` for production/CI runs.

---

## Requests vs browser automation

Don't reach for a browser when a simple HTTP call will do — browsers are heavy.

| Use `requests` when… | Use a browser when… |
|---|---|
| The data is in the raw HTML/JSON | Content is rendered by JavaScript |
| There's a documented API | The site is a single-page app |
| You need speed and low overhead | You must log in through a form / handle sessions |
| No JS execution required | You need to click, scroll, or wait for dynamic loads |

A good workflow: try `requests` first (see [APIs & HTTP](../web/proficient/apis-http.md)); only escalate to a browser if the content isn't in the response.

---

## Ethics & legality

!!! danger "Scrape responsibly"
    Browser automation makes scraping easy — that doesn't make everything legal or acceptable.

    - **Read `robots.txt`** and the site's Terms of Service. Some sites forbid automated access.
    - **Rate-limit yourself.** Add delays; don't hammer a server with rapid-fire requests.
    - **Identify honestly.** Don't impersonate other user agents to evade blocks.
    - **Respect personal data.** Scraping and storing personal information may fall under privacy laws (GDPR, CCPA).
    - **Prefer an official API** when one is offered — it's the sanctioned, stable path.

    When in doubt about a specific site or jurisdiction, get legal advice — this page is technical guidance, not legal counsel.

---

## Practice exercises

1. Use Playwright to open a page, take a full-page screenshot, and save it with `page.screenshot(path=..., full_page=True)`.
2. Write a script that fills and submits a search form, then collects the text of the first five results.
3. Compare speed: time fetching the same static page with `requests` versus a headless browser, and note the difference.
4. Rewrite the Selenium login example in Playwright and note how many explicit waits you were able to remove.
5. Before scraping any real site, check its `robots.txt` and write a short note on what it does and doesn't allow.
