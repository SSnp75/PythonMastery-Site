---
title: Kubernetes Basics
description: Pods, deployments, services, config maps and Python apps on K8s
---

# Kubernetes Basics <span class="pm-badge pm-badge-expert">Expert</span>

<div class="pm-topic-header">
  <strong>🚀 Deployment · Level 6</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisite: <a href="docker/">Docker</a></span>
  </div>
</div>

---

## Core concepts

| Resource | What it does |
|---|---|
| **Pod** | Smallest unit — one or more containers |
| **Deployment** | Manages pod replicas, rolling updates |
| **Service** | Stable network endpoint for pods |
| **ConfigMap** | Configuration data (non-secret) |
| **Secret** | Sensitive data (encoded) |
| **Ingress** | External HTTP routing |

---

## Deploying a Python app

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: myapp
          image: myregistry/myapp:latest
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-secret
                  key: url
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  selector:
    app: myapp
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP
```

```bash
kubectl apply -f deployment.yaml
kubectl get pods
kubectl logs myapp-xxxxx-yyy
kubectl scale deployment myapp --replicas=5
kubectl rollout status deployment/myapp
```

---

## Practice Exercises

1. **Deploy a FastAPI app** to a local k8s cluster (minikube or kind).
2. **Add horizontal pod autoscaling** based on CPU utilization.
3. **Use ConfigMaps and Secrets** for environment configuration.
4. **Set up Ingress** to expose the service with a domain name.
5. **Implement rolling updates** — deploy a new version with zero downtime.
