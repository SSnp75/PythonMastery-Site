---
title: JWT Authentication
description: JSON Web Tokens, access/refresh tokens, middleware and secure implementation
---

# JWT Authentication <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🔐 Auth · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
  </div>
</div>

---

## How JWT works

```
Client                     Server
  │                          │
  ├─── POST /login ──────────►  (verify credentials)
  │    {email, password}     │
  │                          │
  ◄── 200 {access_token, ───┤  (sign JWT with secret)
  │        refresh_token}    │
  │                          │
  ├─── GET /protected ───────►  (verify JWT signature)
  │    Authorization: Bearer │
  │    eyJ...                │
  │                          │
  ◄── 200 {data} ───────────┤
```

---

## Implementation with FastAPI

```python
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI()

# ─── Config ──────────────────────────────────────
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = 30      # minutes
REFRESH_TOKEN_EXPIRE = 7 * 24 * 60   # 7 days

# ─── Password hashing ────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# ─── Token creation ──────────────────────────────
def create_token(data: dict, expires_minutes: int) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(user_id: int) -> str:
    return create_token({"sub": str(user_id), "type": "access"}, ACCESS_TOKEN_EXPIRE)

def create_refresh_token(user_id: int) -> str:
    return create_token({"sub": str(user_id), "type": "refresh"}, REFRESH_TOKEN_EXPIRE)

# ─── Token verification (dependency) ─────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = await get_user_by_id(user_id)   # your DB lookup
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# ─── Routes ──────────────────────────────────────
@app.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = await get_user_by_email(form.username)
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
    }

@app.post("/refresh")
async def refresh(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(400, "Not a refresh token")
        user_id = int(payload["sub"])
    except JWTError:
        raise HTTPException(401, "Invalid refresh token")

    return {"access_token": create_access_token(user_id), "token_type": "bearer"}

@app.get("/profile")
async def profile(user = Depends(get_current_user)):
    return {"id": user.id, "name": user.name, "email": user.email}
```

---

## Role-Based Access Control (RBAC)

```python
from enum import Enum
from functools import wraps

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

def require_role(*roles: Role):
    """Dependency that checks user role."""
    async def role_checker(user = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, admin = Depends(require_role(Role.ADMIN))):
    await db.delete_user(user_id)
    return {"deleted": user_id}

@app.put("/posts/{post_id}/moderate")
async def moderate_post(post_id: int, mod = Depends(require_role(Role.ADMIN, Role.MODERATOR))):
    ...
```

---

## Practice Exercises

1. **Implement registration + login** with password hashing and JWT issuance.
2. **Add refresh token rotation** — issue new refresh token on each refresh.
3. **Implement RBAC** with admin, moderator and user roles.
4. **Add token blacklisting** using Redis (for logout).
5. **Implement rate limiting** on the login endpoint (prevent brute force).
