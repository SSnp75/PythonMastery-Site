---
title: GraphQL
description: Schema definition, resolvers, queries, mutations and Strawberry framework
---

# GraphQL <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🌐 Networking · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~3 days</span>
  </div>
</div>

---

## GraphQL with Strawberry (Python-native)

```python
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI

@strawberry.type
class User:
    id: int
    name: str
    email: str
    age: int

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: int) -> User | None:
        users = {1: User(1, "Alice", "a@b.com", 30), 2: User(2, "Bob", "b@c.com", 25)}
        return users.get(id)

    @strawberry.field
    def users(self) -> list[User]:
        return [User(1, "Alice", "a@b.com", 30), User(2, "Bob", "b@c.com", 25)]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, name: str, email: str, age: int) -> User:
        new_user = User(id=3, name=name, email=email, age=age)
        return new_user

schema = strawberry.Schema(query=Query, mutation=Mutation)

app = FastAPI()
app.include_router(GraphQLRouter(schema), prefix="/graphql")
```

---

## Querying

```graphql
# Get specific fields (no over-fetching!)
query {
  user(id: 1) {
    name
    email
  }
}

# Response:
# {"data": {"user": {"name": "Alice", "email": "a@b.com"}}}

# Get multiple resources in one request
query {
  user(id: 1) { name }
  users { id name }
}

# Mutation
mutation {
  createUser(name: "Charlie", email: "c@d.com", age: 35) {
    id
    name
  }
}
```

---

## REST vs GraphQL

| Feature | REST | GraphQL |
|---|---|---|
| Endpoints | Multiple (`/users`, `/posts`) | Single (`/graphql`) |
| Data shape | Server decides | Client decides |
| Over-fetching | Common | Impossible |
| Under-fetching | Requires multiple calls | Single query |
| Versioning | URL or header | Evolve schema |
| Best for | Simple CRUD, public APIs | Complex UIs, mobile apps |

---

## Practice Exercises

1. **Build a GraphQL API** for a blog (posts, comments, authors) with Strawberry.
2. **Implement pagination** with cursor-based connections.
3. **Add authentication** — only logged-in users can mutate data.
4. **Implement DataLoader** to solve the N+1 problem in resolvers.
5. **Compare** a GraphQL API vs REST API for the same data — measure payload sizes.
