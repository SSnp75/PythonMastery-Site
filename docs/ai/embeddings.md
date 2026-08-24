---
title: Embeddings & Vector Databases
description: Text embeddings, similarity search, ChromaDB, Pinecone, pgvector and semantic search
---

# Embeddings & Vector Databases <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🤖 AI Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
    <span>📚 Prerequisite: <a href="../../data/intermediate/numpy/">NumPy</a></span>
  </div>
</div>

---

## What are embeddings?

Embeddings are **dense vector representations** of text (or images, audio) where semantically similar items are close in vector space.

```python
from openai import OpenAI
import numpy as np

client = OpenAI()

def embed(texts: list[str]) -> np.ndarray:
    response = client.embeddings.create(input=texts, model="text-embedding-3-small")
    return np.array([item.embedding for item in response.data])

# Similar sentences → similar vectors
vecs = embed([
    "The cat sat on the mat",          # about cats
    "A kitten was sleeping on the rug", # about cats (similar!)
    "Stock prices rose 5% today",       # about finance (different!)
])

def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print(f"Cat sentences: {cosine_sim(vecs[0], vecs[1]):.4f}")   # ~0.85 (high!)
print(f"Cat vs finance: {cosine_sim(vecs[0], vecs[2]):.4f}")  # ~0.15 (low!)
```

---

## Local embeddings (no API needed)

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")   # 384 dimensions, fast

texts = ["Python is great", "I love coding in Python", "The weather is nice"]
embeddings = model.encode(texts)

print(embeddings.shape)   # (3, 384)
# Similarity computed same way as above
```

---

## ChromaDB (local vector database)

```python
import chromadb

client = chromadb.PersistentClient(path="./my_vectordb")
collection = client.get_or_create_collection("documents")

# Add documents (auto-embeds with default model)
collection.add(
    documents=["Python is a programming language", "JavaScript runs in browsers", "Rust is memory-safe"],
    metadatas=[{"lang": "python"}, {"lang": "javascript"}, {"lang": "rust"}],
    ids=["doc1", "doc2", "doc3"],
)

# Query
results = collection.query(query_texts=["What language is safe?"], n_results=2)
print(results["documents"][0])   # ['Rust is memory-safe', ...]
print(results["distances"][0])   # [0.45, 0.89]  (lower = more similar)

# Filter by metadata
results = collection.query(
    query_texts=["programming"],
    n_results=5,
    where={"lang": "python"},   # only search Python docs
)
```

---

## pgvector (PostgreSQL extension)

```python
import psycopg
from pgvector.psycopg import register_vector

conn = psycopg.connect("postgresql://localhost/mydb")
register_vector(conn)

# Create table with vector column
conn.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        content TEXT,
        embedding vector(1536)
    )
""")

# Insert
conn.execute(
    "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
    ("Python is great", embedding_vector)
)

# Similarity search (cosine distance)
results = conn.execute("""
    SELECT content, 1 - (embedding <=> %s::vector) AS similarity
    FROM documents
    ORDER BY embedding <=> %s::vector
    LIMIT 5
""", (query_embedding, query_embedding)).fetchall()

for content, similarity in results:
    print(f"  {similarity:.4f}: {content}")
```

---

## Pinecone (managed cloud vector DB)

```python
from pinecone import Pinecone

pc = Pinecone(api_key="your-key")
index = pc.Index("my-index")

# Upsert vectors
index.upsert(vectors=[
    {"id": "doc1", "values": embedding1, "metadata": {"source": "wiki"}},
    {"id": "doc2", "values": embedding2, "metadata": {"source": "blog"}},
])

# Query
results = index.query(vector=query_embedding, top_k=5, include_metadata=True)
for match in results["matches"]:
    print(f"  {match['id']}: score={match['score']:.4f}, source={match['metadata']['source']}")
```

---

## Choosing a vector database

| Database | Type | Best for | Scale |
|---|---|---|---|
| **ChromaDB** | Embedded/local | Prototyping, small datasets | <1M vectors |
| **pgvector** | PostgreSQL extension | Existing Postgres stack | <10M vectors |
| **Pinecone** | Managed cloud | Production, no-ops | Billions |
| **Weaviate** | Self-hosted/cloud | Multi-modal, GraphQL | Millions |
| **Qdrant** | Self-hosted/cloud | Performance, filtering | Billions |
| **FAISS** | Library (in-process) | Research, batch processing | Billions |

---

## Practice Exercises

1. **Build a semantic search engine** over your notes — query in natural language.
2. **Compare embedding models** — OpenAI vs sentence-transformers on a retrieval task.
3. **Implement approximate nearest neighbors** with FAISS and compare speed vs exact search.
4. **Build a duplicate detector** — find near-duplicate documents using cosine similarity.
5. **Use pgvector** to add semantic search to an existing PostgreSQL application.
6. **Build a recommendation system** — "users who liked X also liked Y" using item embeddings.
