---
title: Secrets Management
description: Environment variables, HashiCorp Vault, AWS Secrets Manager and secure configuration
---

# Secrets Management <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🔒 Security & DevOps Track · Level 6</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
  </div>
</div>

---

## The rules

1. **NEVER** hardcode secrets in source code
2. **NEVER** commit `.env` files to git
3. **ALWAYS** use environment variables or a secrets manager
4. **ROTATE** secrets regularly
5. **AUDIT** who accessed which secret and when
6. **ENCRYPT** secrets at rest and in transit

---

## Environment variables (simplest approach)

```python
import os

# Read from environment
db_password = os.environ["DB_PASSWORD"]       # raises KeyError if missing
api_key = os.environ.get("API_KEY", "")       # returns "" if missing

# Validate required secrets at startup
REQUIRED = ["DB_PASSWORD", "API_KEY", "JWT_SECRET"]
missing = [k for k in REQUIRED if k not in os.environ]
if missing:
    raise RuntimeError(f"Missing required env vars: {missing}")
```

### python-dotenv (for local development)

```python
# .env file (NEVER commit this!)
# DB_PASSWORD=super_secret_123
# API_KEY=sk_live_abc123

from dotenv import load_dotenv
load_dotenv()   # loads .env into os.environ

db_pass = os.environ["DB_PASSWORD"]
```

```gitignore
# .gitignore
.env
.env.local
.env.production
```

---

## Pydantic Settings (type-safe config)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_password: str           # required — no default
    api_key: str
    jwt_secret: str
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
# Automatically reads from environment variables
# Validates types (int, bool, etc.)
# Raises clear errors if required vars are missing
print(settings.db_host)       # localhost
print(settings.db_password)   # from env
```

---

## AWS Secrets Manager

```python
import boto3
import json

def get_secret(secret_name: str, region: str = "us-east-1") -> dict:
    client = boto3.client("secretsmanager", region_name=region)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])

# Usage
db_creds = get_secret("production/database")
print(db_creds["username"])
print(db_creds["password"])

# With caching (avoid hitting API every time)
from functools import lru_cache

@lru_cache(maxsize=32)
def get_secret_cached(secret_name: str) -> dict:
    return get_secret(secret_name)
```

---

## HashiCorp Vault

```python
import hvac

client = hvac.Client(url="https://vault.example.com:8200", token=os.environ["VAULT_TOKEN"])

# Read a secret
secret = client.secrets.kv.v2.read_secret_version(path="myapp/database")
db_password = secret["data"]["data"]["password"]

# Write a secret
client.secrets.kv.v2.create_or_update_secret(
    path="myapp/api-keys",
    secret={"stripe": "sk_live_...", "sendgrid": "SG..."},
)

# Dynamic secrets (Vault generates temporary credentials)
creds = client.secrets.database.generate_credentials(name="my-role")
print(f"Username: {creds['data']['username']}")
print(f"Password: {creds['data']['password']}")
# These expire automatically!
```

---

## Secret rotation pattern

```python
import secrets
import boto3
from datetime import datetime, timedelta

class SecretRotator:
    def __init__(self, secret_name: str):
        self.client = boto3.client("secretsmanager")
        self.secret_name = secret_name

    def rotate(self):
        # Generate new secret
        new_password = secrets.token_urlsafe(32)

        # Update in secrets manager
        self.client.update_secret(
            SecretId=self.secret_name,
            SecretString=new_password,
        )

        # Update the actual service (database, API, etc.)
        self._update_service(new_password)

        # Log rotation
        print(f"  Rotated {self.secret_name} at {datetime.utcnow().isoformat()}")

    def _update_service(self, new_password):
        # Implementation depends on what the secret is for
        pass
```

---

## Practice Exercises

1. **Set up python-dotenv** with validation for a project with 10+ config variables.
2. **Use Pydantic Settings** with environment-specific overrides (dev, staging, prod).
3. **Integrate AWS Secrets Manager** into a FastAPI app with caching.
4. **Implement secret rotation** that generates new API keys and updates all services.
5. **Build a secrets audit log** that records every access with timestamp and requester.
6. **Create a `.env.example`** template generator that documents all required variables.
