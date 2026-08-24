---
title: RAG (Retrieval-Augmented Generation)
description: Build systems that ground LLM responses in your own data — chunking, embeddings, retrieval and generation
---

# RAG <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🤖 AI Track · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="llm-apis/">LLM APIs</a>, <a href="embeddings/">Embeddings</a></span>
  </div>
</div>

---

## What is RAG?

RAG combines retrieval (search your documents) with generation (LLM produces answer) so the model responds using **your data** instead of hallucinating.

```
User Question → Embed → Search Vector DB → Top K chunks → LLM (question + context) → Answer
```

---

## Full RAG pipeline from scratch

### Step 1: Load and chunk documents

```python
from pathlib import Path

def load_documents(directory: str) -> list[dict]:
    """Load text files from a directory."""
    docs = []
    for path in Path(directory).glob("**/*.txt"):
        docs.append({
            "source": str(path),
            "content": path.read_text(encoding="utf-8"),
        })
    return docs

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind(".")
            if last_period > chunk_size * 0.5:
                end = start + last_period + 1
                chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
    return [c for c in chunks if c]

# Usage
docs = load_documents("./knowledge_base")
all_chunks = []
for doc in docs:
    chunks = chunk_text(doc["content"])
    for chunk in chunks:
        all_chunks.append({"text": chunk, "source": doc["source"]})

print(f"Loaded {len(docs)} documents → {len(all_chunks)} chunks")
```

### Step 2: Generate embeddings

```python
from openai import OpenAI
import numpy as np

client = OpenAI()

def get_embeddings(texts: list[str], model="text-embedding-3-small") -> list[list[float]]:
    """Get embeddings from OpenAI API."""
    response = client.embeddings.create(input=texts, model=model)
    return [item.embedding for item in response.data]

# Embed all chunks (batch for efficiency)
batch_size = 100
all_embeddings = []
for i in range(0, len(all_chunks), batch_size):
    batch = [c["text"] for c in all_chunks[i:i+batch_size]]
    embeddings = get_embeddings(batch)
    all_embeddings.extend(embeddings)
    print(f"  Embedded {min(i+batch_size, len(all_chunks))}/{len(all_chunks)}")

# Store as numpy array
embedding_matrix = np.array(all_embeddings)
print(f"Embedding matrix shape: {embedding_matrix.shape}")  # (n_chunks, 1536)
```

### Step 3: Search (retrieval)

```python
def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search(query: str, top_k: int = 5) -> list[dict]:
    """Find most relevant chunks for a query."""
    query_embedding = get_embeddings([query])[0]
    query_vec = np.array(query_embedding)

    # Compute similarity with all chunks
    similarities = np.dot(embedding_matrix, query_vec) / (
        np.linalg.norm(embedding_matrix, axis=1) * np.linalg.norm(query_vec)
    )

    # Get top K
    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in top_indices:
        results.append({
            "text": all_chunks[idx]["text"],
            "source": all_chunks[idx]["source"],
            "score": float(similarities[idx]),
        })
    return results
```

### Step 4: Generate answer

```python
def ask(question: str, top_k: int = 5) -> str:
    """Full RAG: retrieve relevant chunks, then generate answer."""
    # Retrieve
    results = search(question, top_k=top_k)

    # Build context
    context = "\n\n---\n\n".join([
        f"[Source: {r['source']}]\n{r['text']}" for r in results
    ])

    # Generate
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": (
                "Answer the user's question based ONLY on the provided context. "
                "If the context doesn't contain the answer, say 'I don't have "
                "enough information to answer this.' Cite sources."
            )},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.2,   # low temperature for factual answers
    )
    return response.choices[0].message.content

# Usage
answer = ask("How do Python decorators work?")
print(answer)
# "Based on the documentation [Source: docs/decorators.txt], Python decorators
#  are functions that wrap other functions to modify their behavior..."
```

---

## Using a vector database (ChromaDB)

```python
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

# Initialize
embedding_fn = OpenAIEmbeddingFunction(api_key="sk-...", model_name="text-embedding-3-small")
chroma = chromadb.PersistentClient(path="./chroma_db")
collection = chroma.get_or_create_collection("knowledge_base", embedding_function=embedding_fn)

# Add documents
collection.add(
    documents=[c["text"] for c in all_chunks],
    metadatas=[{"source": c["source"]} for c in all_chunks],
    ids=[f"chunk_{i}" for i in range(len(all_chunks))],
)

# Query
results = collection.query(
    query_texts=["How do decorators work?"],
    n_results=5,
)
for doc, meta, distance in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
    print(f"  [{meta['source']}] (distance: {distance:.4f})")
    print(f"  {doc[:100]}...")
```

---

## LangChain RAG (higher-level)

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import DirectoryLoader

# Load
loader = DirectoryLoader("./docs", glob="**/*.txt")
documents = loader.load()

# Split
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documents)

# Embed and store
vectorstore = Chroma.from_documents(chunks, OpenAIEmbeddings(), persist_directory="./db")

# Build RAG chain
qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4o", temperature=0),
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True,
)

# Ask
result = qa.invoke({"query": "How do decorators work?"})
print(result["result"])
for doc in result["source_documents"]:
    print(f"  Source: {doc.metadata['source']}")
```

---

## RAG optimization techniques

| Technique | What it does |
|---|---|
| **Hybrid search** | Combine vector search + keyword (BM25) |
| **Re-ranking** | Score results with a cross-encoder after retrieval |
| **Query expansion** | Generate multiple query variants for broader recall |
| **Contextual chunking** | Include document title/headers in each chunk |
| **Metadata filtering** | Filter by date, source, category before vector search |
| **Multi-step RAG** | First retrieve docs, then extract relevant passages |

---

## Practice Exercises

1. **Build a RAG system** over your own notes/docs — ask questions, get grounded answers.
2. **Compare chunking strategies** — fixed size vs sentence-based vs paragraph-based. Measure retrieval quality.
3. **Implement hybrid search** — combine vector similarity with keyword BM25 scoring.
4. **Add re-ranking** with a cross-encoder model to improve result quality.
5. **Build a conversational RAG** that maintains chat history and reformulates follow-up questions.
6. **Evaluate RAG quality** — create a test set of questions with known answers, measure precision/recall.
