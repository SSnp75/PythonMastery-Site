---
title: NLP Fundamentals
description: Tokenization, text preprocessing, spaCy, transformers and text classification
---

# NLP Fundamentals <span class="pm-badge pm-badge-intermediate">Intermediate</span>

<div class="pm-topic-header">
  <strong>🤖 AI Track · Level 3</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prerequisites: <a href="../data/intermediate/numpy/">NumPy</a>, <a href="../data/intermediate/pandas/">Pandas</a></span>
  </div>
</div>

---

## Text preprocessing pipeline

```python
import re
from collections import Counter

def preprocess(text: str) -> list[str]:
    """Standard NLP preprocessing pipeline."""
    text = text.lower()                              # lowercase
    text = re.sub(r'[^\w\s]', '', text)             # remove punctuation
    text = re.sub(r'\d+', '', text)                 # remove numbers
    tokens = text.split()                            # tokenize (simple)
    # Remove stopwords
    stopwords = {"the", "a", "an", "is", "are", "was", "in", "on", "at", "to", "for", "of", "and", "or"}
    tokens = [t for t in tokens if t not in stopwords and len(t) > 2]
    return tokens

text = "The cat sat on the mat. Cats are wonderful animals!"
tokens = preprocess(text)
print(tokens)   # ['cat', 'sat', 'mat', 'cats', 'wonderful', 'animals']

# Word frequencies
freq = Counter(tokens)
print(freq.most_common(5))
```

---

## spaCy — industrial NLP

```python
import spacy

nlp = spacy.load("en_core_web_sm")

doc = nlp("Apple is looking at buying a UK startup for $1 billion.")

# ─── Tokenization ─────────────────────────────────
for token in doc:
    print(f"{token.text:12} {token.pos_:6} {token.dep_:10} {token.lemma_}")
# Apple        PROPN  nsubj      Apple
# is           AUX    aux        be
# looking      VERB   ROOT       look
# at           ADP    prep       at
# buying       VERB   pcomp      buy
# ...

# ─── Named Entity Recognition ────────────────────
for ent in doc.ents:
    print(f"  {ent.text:20} → {ent.label_}")
# Apple                → ORG
# UK                   → GPE
# $1 billion           → MONEY

# ─── Sentence segmentation ───────────────────────
text = "I love Python. It's great for NLP. Let's use it!"
doc = nlp(text)
for sent in doc.sents:
    print(f"  Sentence: {sent.text}")

# ─── Similarity ──────────────────────────────────
doc1 = nlp("I love programming")
doc2 = nlp("Coding is my passion")
doc3 = nlp("The weather is nice")
print(f"Similar: {doc1.similarity(doc2):.3f}")     # ~0.7
print(f"Different: {doc1.similarity(doc3):.3f}")   # ~0.2
```

---

## Hugging Face Transformers

```python
from transformers import pipeline

# ─── Sentiment Analysis ───────────────────────────
classifier = pipeline("sentiment-analysis")
result = classifier("I absolutely love this product! Best purchase ever.")
print(result)   # [{'label': 'POSITIVE', 'score': 0.9998}]

# ─── Text Classification ─────────────────────────
classifier = pipeline("zero-shot-classification")
result = classifier(
    "This code has a critical security vulnerability",
    candidate_labels=["security", "performance", "documentation", "bug"],
)
print(result["labels"][0])    # security
print(result["scores"][0])   # 0.92

# ─── Named Entity Recognition ────────────────────
ner = pipeline("ner", grouped_entities=True)
result = ner("Elon Musk founded SpaceX in Hawthorne, California")
for entity in result:
    print(f"  {entity['word']:20} → {entity['entity_group']} ({entity['score']:.3f})")
# Elon Musk            → PER (0.998)
# SpaceX               → ORG (0.997)
# Hawthorne, California → LOC (0.995)

# ─── Summarization ───────────────────────────────
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
long_text = "..." # your long article
summary = summarizer(long_text, max_length=130, min_length=30)
print(summary[0]["summary_text"])

# ─── Question Answering ──────────────────────────
qa = pipeline("question-answering")
result = qa(
    question="What is the capital of France?",
    context="France is a country in Europe. Paris is the capital of France."
)
print(result)   # {'answer': 'Paris', 'score': 0.99, 'start': 42, 'end': 47}
```

---

## Text classification from scratch

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

# Data
texts = ["This movie is great", "Terrible film", "Loved it", "Waste of time", ...]
labels = [1, 0, 1, 0, ...]   # 1=positive, 0=negative

X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2)

# TF-IDF + Logistic Regression pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
    ("clf", LogisticRegression(max_iter=1000)),
])

model.fit(X_train, y_train)
score = model.score(X_test, y_test)
print(f"Accuracy: {score:.4f}")   # ~0.85

# Predict new text
predictions = model.predict(["This is absolutely wonderful!"])
print(predictions)   # [1] (positive)
```

---

## Practice Exercises

1. **Build a spam classifier** using TF-IDF + logistic regression on the SMS Spam dataset.
2. **Extract entities** from news articles using spaCy and group by entity type.
3. **Build a sentiment analyzer** for product reviews using Hugging Face pipelines.
4. **Implement TF-IDF from scratch** and compare with sklearn's implementation.
5. **Build a text similarity search** — given a query, find the most similar documents.
6. **Fine-tune a classifier** — use a pre-trained transformer for domain-specific classification.
