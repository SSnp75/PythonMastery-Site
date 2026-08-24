---
title: Database Design
description: Normalization, schema design, relationships, indexes and data modeling
---

# Database Design <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🗄️ Databases · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
  </div>
</div>

---

## Normalization forms

| Form | Rule | Example fix |
|---|---|---|
| **1NF** | No repeating groups, atomic values | Split "tags: python,java" → tag table |
| **2NF** | No partial dependencies on composite key | Move non-key-dependent columns to own table |
| **3NF** | No transitive dependencies | If A→B→C, move C to B's table |

---

## Relationship patterns

```sql
-- One-to-Many (most common)
CREATE TABLE authors (id SERIAL PRIMARY KEY, name TEXT);
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title TEXT,
    author_id INTEGER REFERENCES authors(id)
);

-- Many-to-Many (junction table)
CREATE TABLE students (id SERIAL PRIMARY KEY, name TEXT);
CREATE TABLE courses (id SERIAL PRIMARY KEY, title TEXT);
CREATE TABLE enrollments (
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id),
    enrolled_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (student_id, course_id)
);

-- One-to-One
CREATE TABLE users (id SERIAL PRIMARY KEY, email TEXT UNIQUE);
CREATE TABLE profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    bio TEXT,
    avatar_url TEXT
);
```

---

## Common schema patterns

### Soft delete
```sql
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP NULL;
-- Query: WHERE deleted_at IS NULL
```

### Audit trail
```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT,
    record_id INTEGER,
    action TEXT,   -- INSERT, UPDATE, DELETE
    old_data JSONB,
    new_data JSONB,
    changed_by INTEGER,
    changed_at TIMESTAMP DEFAULT NOW()
);
```

### Polymorphic associations
```sql
-- Instead of separate foreign keys per type:
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    body TEXT,
    commentable_type TEXT,   -- 'post', 'photo', 'video'
    commentable_id INTEGER,
    created_at TIMESTAMP
);
CREATE INDEX idx_commentable ON comments(commentable_type, commentable_id);
```

---

## Practice Exercises

1. **Design a schema** for an e-commerce platform (users, products, orders, reviews, categories).
2. **Normalize** a denormalized spreadsheet into 3NF tables.
3. **Add indexes** and justify each one based on expected query patterns.
4. **Design for scale** — partition a large table by date range.
5. **Compare** normalized vs denormalized schema for read-heavy vs write-heavy workloads.
