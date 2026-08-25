# Python Mastery — Q&A Backend (Phase 2)

Custom Q&A system to replace/complement Giscus when the site grows.

## Architecture

```
┌─────────────────────┐        ┌──────────────────┐        ┌──────────────┐
│  MkDocs Static Site │  JS ──►│  FastAPI Backend  │  SQL ──►│  PostgreSQL  │
│  (GitHub Pages)     │◄── API │  /api/v1/...      │◄────────│              │
│  + Giscus (Phase 1) │        │                   │        └──────────────┘
└─────────────────────┘        │  Auth: GitHub     │        ┌──────────────┐
                               │  OAuth2           │  Cache ►│  Redis       │
                               └──────────────────┘        └──────────────┘
```

## When to switch from Giscus to this

- 50+ active discussions
- Non-GitHub users need to participate  
- Need features: upvoting, accepted answers, reputation, tags, search
- Want full data ownership

## Features (planned)

- [x] API design (below)
- [ ] User auth (GitHub OAuth2)
- [ ] Questions (per-page, tags, status)
- [ ] Answers (per-question, accept, upvote)
- [ ] Comments (on questions and answers)
- [ ] Voting (questions, answers)
- [ ] Search (full-text across all Q&A)
- [ ] Moderation (flag, hide, ban)
- [ ] Notifications (email digest)
- [ ] Embed widget (JS snippet for static site)

## API Design

### Endpoints

```
POST   /api/v1/auth/github          — OAuth2 callback, issue JWT
GET    /api/v1/auth/me              — current user profile

GET    /api/v1/questions?page_path=core/decorators&page=1
POST   /api/v1/questions            — ask a question
GET    /api/v1/questions/{id}       — question detail + answers
PATCH  /api/v1/questions/{id}       — edit question (author only)
DELETE /api/v1/questions/{id}       — delete (author/admin)

POST   /api/v1/questions/{id}/answers      — post an answer
PATCH  /api/v1/answers/{id}                — edit answer
DELETE /api/v1/answers/{id}                — delete
POST   /api/v1/answers/{id}/accept         — mark as accepted (question author)

POST   /api/v1/questions/{id}/comments     — comment on question
POST   /api/v1/answers/{id}/comments       — comment on answer
DELETE /api/v1/comments/{id}               — delete comment

POST   /api/v1/questions/{id}/vote         — upvote/downvote question
POST   /api/v1/answers/{id}/vote           — upvote/downvote answer

GET    /api/v1/search?q=decorators&page=1  — full-text search
```

### Data Models

```
User
  id, github_id, username, avatar_url, reputation, role, created_at

Question
  id, user_id, page_path, title, body (markdown), tags[], 
  vote_count, answer_count, accepted_answer_id, status, created_at, updated_at

Answer  
  id, question_id, user_id, body (markdown), vote_count, 
  is_accepted, created_at, updated_at

Comment
  id, user_id, parent_type (question/answer), parent_id, body, created_at

Vote
  id, user_id, target_type, target_id, value (+1/-1), created_at
```

## Tech Stack

- **FastAPI** — async API framework
- **SQLAlchemy 2.0** — async ORM  
- **PostgreSQL** — primary database
- **Redis** — caching, rate limiting
- **Alembic** — migrations
- **python-jose** — JWT tokens
- **authlib** — GitHub OAuth2

## Run locally

```bash
cd backend
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

## Deploy

```bash
docker compose up -d   # backend + postgres + redis
```
