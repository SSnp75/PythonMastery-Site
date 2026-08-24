---
title: OAuth2 & SSO
description: OAuth2 authorization code flow, Google/GitHub login and Single Sign-On
---

# OAuth2 & SSO <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🔐 Auth · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
  </div>
</div>

---

## OAuth2 Authorization Code Flow

```
User → Your App → Redirect to Provider (Google/GitHub)
     → User logs in at Provider
     → Provider redirects back with ?code=abc
     → Your App exchanges code for access_token
     → Your App calls Provider API with access_token
     → Gets user info → Creates/logs in user
```

---

## Implementation with authlib

```python
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth

app = FastAPI()

oauth = OAuth()
oauth.register(
    name="github",
    client_id="your-client-id",
    client_secret="your-client-secret",
    authorize_url="https://github.com/login/oauth/authorize",
    access_token_url="https://github.com/login/oauth/access_token",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)

@app.get("/login/github")
async def login_github(request: Request):
    redirect_uri = "http://localhost:8000/callback/github"
    return await oauth.github.authorize_redirect(request, redirect_uri)

@app.get("/callback/github")
async def callback_github(request: Request):
    token = await oauth.github.authorize_access_token(request)
    user_info = await oauth.github.get("user", token=token)
    user_data = user_info.json()

    # Create or find user in your database
    user = await find_or_create_user(
        provider="github",
        provider_id=str(user_data["id"]),
        email=user_data.get("email"),
        name=user_data["name"],
        avatar=user_data["avatar_url"],
    )

    # Issue your own JWT
    access_token = create_access_token(user.id)
    return {"access_token": access_token, "user": user.name}
```

---

## Practice Exercises

1. **Implement "Login with GitHub"** — full OAuth2 flow.
2. **Support multiple providers** — Google, GitHub and email/password all linking to one user.
3. **Implement PKCE** (Proof Key for Code Exchange) for mobile/SPA apps.
4. **Build an OAuth2 provider** — your app issues tokens for third-party apps.
