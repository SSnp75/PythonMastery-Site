# Giscus Setup Guide

## Steps to activate Giscus comments on your site

### 1. Create a public GitHub repository

Create a repo (e.g., `your-username/pythonmastery`) and make sure it's **public**.

### 2. Enable GitHub Discussions

Go to: Repo → Settings → Features → check "Discussions"

Create a Discussion category called **"Comments"** (Announcement type recommended).

### 3. Install the Giscus app

Go to: https://github.com/apps/giscus → Install → select your repo

### 4. Get your configuration

Go to: https://giscus.app

Fill in:
- **Repository:** `your-username/pythonmastery`
- **Page ↔ Discussion mapping:** `pathname` (each page URL gets its own discussion)
- **Category:** `Comments`
- **Theme:** `preferred_color_scheme` (adapts to light/dark)
- **Input position:** `top` (comment box at top for easy access)
- **Loading:** `lazy`

The tool generates a `<script>` tag. Copy the `data-repo-id` and `data-category-id`.

### 5. Update the site template

Edit `overrides/partials/comments.html` and replace:
- `data-repo="YOUR_GITHUB_USERNAME/pythonmastery"` → your actual repo
- `data-repo-id=""` → the value from giscus.app
- `data-category-id=""` → the value from giscus.app

### 6. Rebuild and deploy

```bash
py -m mkdocs build
py -m mkdocs gh-deploy
```

### 7. Test it

Open any topic page → scroll to the bottom → you should see the Giscus comment widget. Sign in with GitHub and leave a test comment.

---

## Disable comments on specific pages

Add to the page's frontmatter:

```yaml
---
hide_comments: true
---
```

---

## What happens next (Phase 2)

When the site grows and you want more control, the custom Q&A backend in `backend/` replaces Giscus. See `backend/README.md` for the full API design.
