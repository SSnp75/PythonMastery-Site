---
title: Python for DevOps
description: Docker SDK, Fabric, infrastructure automation, CI/CD and subprocess management
---

# Python for DevOps <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🔒 Security & DevOps Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="../../core/competent/standard-library/">Standard Library</a></span>
  </div>
</div>

---

## subprocess — running system commands

```python
import subprocess

# Simple command
result = subprocess.run(
    ["git", "log", "--oneline", "-5"],
    capture_output=True, text=True, check=True, timeout=30,
)
print(result.stdout)
print(f"Exit code: {result.returncode}")

# Error handling
try:
    subprocess.run(["false"], check=True)
except subprocess.CalledProcessError as e:
    print(f"Command failed with code {e.returncode}")
    print(f"Stderr: {e.stderr}")

# Streaming output (for long-running commands)
process = subprocess.Popen(
    ["ping", "-c", "5", "google.com"],
    stdout=subprocess.PIPE, text=True,
)
for line in process.stdout:
    print(f"  {line.strip()}")
process.wait()
```

---

## Docker SDK

```python
import docker

client = docker.from_env()

# ─── Images ──────────────────────────────────────
# Pull an image
client.images.pull("python:3.13-slim")

# List images
for img in client.images.list():
    print(f"  {img.tags}: {img.short_id}")

# Build from Dockerfile
image, logs = client.images.build(path="./my_app", tag="my_app:latest")
for chunk in logs:
    if "stream" in chunk:
        print(chunk["stream"], end="")

# ─── Containers ──────────────────────────────────
# Run container (blocking)
output = client.containers.run(
    "python:3.13-slim",
    command="python -c 'print(2**100)'",
    remove=True,
)
print(output.decode())   # 1267650600228229401496703205376

# Run detached
container = client.containers.run(
    "nginx:latest",
    detach=True,
    ports={"80/tcp": 8080},
    name="my_nginx",
)
print(f"Container {container.short_id} running")

# Inspect
print(container.status)          # running
print(container.logs().decode()) # container logs

# Stop and remove
container.stop()
container.remove()

# ─── Docker Compose (programmatic) ───────────────
# List running containers
for c in client.containers.list():
    print(f"  {c.name}: {c.status} ({c.image.tags})")

# Prune unused resources
client.containers.prune()
client.images.prune()
client.volumes.prune()
```

---

## Fabric — remote SSH execution

```python
from fabric import Connection, task

# Connect to remote server
conn = Connection(
    host="deploy.example.com",
    user="deploy",
    connect_kwargs={"key_filename": "~/.ssh/id_rsa"},
)

# Run commands
result = conn.run("uname -a", hide=True)
print(result.stdout.strip())

# Upload/download files
conn.put("local_file.py", "/remote/path/file.py")
conn.get("/remote/path/output.log", "local_output.log")

# Run with sudo
conn.sudo("systemctl restart my-app")

# Deployment script
def deploy(conn):
    with conn.cd("/opt/myapp"):
        conn.run("git pull origin main")
        conn.run("pip install -r requirements.txt")
        conn.sudo("systemctl restart myapp")
        # Verify
        result = conn.run("curl -s http://localhost:8000/health")
        assert "ok" in result.stdout
        print("  Deploy successful!")

deploy(conn)
```

---

## CI/CD with Python

### GitHub Actions (generate workflow from Python)

```python
import yaml

workflow = {
    "name": "CI",
    "on": {"push": {"branches": ["main"]}, "pull_request": {}},
    "jobs": {
        "test": {
            "runs-on": "ubuntu-latest",
            "strategy": {"matrix": {"python-version": ["3.11", "3.12", "3.13"]}},
            "steps": [
                {"uses": "actions/checkout@v4"},
                {"name": "Set up Python", "uses": "actions/setup-python@v5",
                 "with": {"python-version": "${{ matrix.python-version }}"}},
                {"name": "Install", "run": "pip install -e .[test]"},
                {"name": "Lint", "run": "ruff check ."},
                {"name": "Test", "run": "pytest --cov=src tests/"},
                {"name": "Type check", "run": "mypy src/"},
            ],
        },
        "deploy": {
            "needs": "test",
            "if": "github.ref == 'refs/heads/main'",
            "runs-on": "ubuntu-latest",
            "steps": [
                {"uses": "actions/checkout@v4"},
                {"name": "Deploy", "run": "python deploy.py"},
            ],
        },
    },
}

with open(".github/workflows/ci.yml", "w") as f:
    yaml.dump(workflow, f, default_flow_style=False, sort_keys=False)
```

---

## Infrastructure as Code patterns

```python
# Declarative infrastructure definition
from dataclasses import dataclass

@dataclass
class Server:
    name: str
    provider: str
    region: str
    size: str
    image: str
    ssh_keys: list[str]

@dataclass
class Infrastructure:
    servers: list[Server]
    load_balancer: dict
    database: dict

infra = Infrastructure(
    servers=[
        Server("web-1", "digitalocean", "nyc1", "s-2vcpu-4gb", "ubuntu-22-04", ["my-key"]),
        Server("web-2", "digitalocean", "nyc1", "s-2vcpu-4gb", "ubuntu-22-04", ["my-key"]),
    ],
    load_balancer={"name": "lb-1", "algorithm": "round_robin", "health_check": "/health"},
    database={"engine": "postgres", "version": "16", "size": "db-s-1vcpu-2gb"},
)

def provision(infra: Infrastructure):
    for server in infra.servers:
        print(f"  Provisioning {server.name} ({server.size}) in {server.region}")
        # API calls to cloud provider...
```

---

## Monitoring and alerting

```python
import psutil
import smtplib
from datetime import datetime

def check_system_health() -> dict:
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "load_avg": psutil.getloadavg(),
    }

def alert_if_critical(health: dict, thresholds: dict):
    alerts = []
    if health["cpu_percent"] > thresholds.get("cpu", 90):
        alerts.append(f"CPU at {health['cpu_percent']}%")
    if health["memory_percent"] > thresholds.get("memory", 85):
        alerts.append(f"Memory at {health['memory_percent']}%")
    if health["disk_percent"] > thresholds.get("disk", 90):
        alerts.append(f"Disk at {health['disk_percent']}%")
    return alerts

health = check_system_health()
alerts = alert_if_critical(health, {"cpu": 80, "memory": 80, "disk": 90})
if alerts:
    print(f"ALERT: {', '.join(alerts)}")
```

---

## Practice Exercises

1. **Write a deployment script** using Fabric that deploys to 3 servers with rollback on failure.
2. **Build a Docker image** programmatically with the Docker SDK and push to a registry.
3. **Create a CI/CD pipeline** generator that produces GitHub Actions YAML from a Python config.
4. **Build a server health monitor** that checks CPU/memory/disk every 30s and sends alerts.
5. **Write a log rotator** that archives old logs, compresses them and cleans up.
6. **Implement blue-green deployment** — script that switches traffic between two server groups.
