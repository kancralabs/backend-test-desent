# Books API - 8 Level Challenge

Production-ready REST API built with **FastAPI + PostgreSQL**, featuring JWT authentication, cursor-based pagination, and async SQLAlchemy 2.0.

**Performance target**: <50ms queries at 1M+ rows

---

## Features

- FastAPI with async/await
- PostgreSQL with async SQLAlchemy 2.0
- JWT authentication (Level 5)
- Cursor-based pagination (Level 6)
- Proper database indexing for high performance
- Docker development environment
- Alembic migrations
- Swagger UI documentation

---

## Quick Start

### 1. Clone & Setup

```bash
# Copy environment variables
cp .env.example .env

# Edit .env if needed (default values work for local development)
```

### 2. Start Services

```bash
# Build and start PostgreSQL + FastAPI
docker-compose up --build

# Wait for "Books API starting up..." message
# Docs available at: http://localhost:8000/docs
```

### 3. Run Migrations

In a new terminal:

```bash
# Enter app container
docker exec -it books_api bash

# Generate initial migration
alembic revision --autogenerate -m "Create books table with indexes"

# Apply migration
alembic upgrade head

# Exit container
exit
```

### 4. Access API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/api/v1/ping

---

## 8 Level Challenge - Testing Guide

### Level 1: Ping

```bash
curl http://localhost:8000/api/v1/ping
# Expected: {"message": "pong"}
```

### Level 2: Echo

```bash
curl -X POST http://localhost:8000/api/v1/echo \
  -H "Content-Type: application/json" \
  -d '{"test": "data", "number": 123}'
# Expected: {"test": "data", "number": 123}
```

### Level 5: Authentication

**Demo credentials:**
- Username: `admin`
- Password: `secret123`

```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secret123"}'
# Expected: {"access_token": "eyJ...", "token_type": "bearer"}

# Save token for next requests
export TOKEN="<access_token>"
```

### Level 3: Create & Read Books

**Create book:**
```bash
curl -X POST http://localhost:8000/api/v1/books \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert Martin",
    "published_year": 2008
  }'
# Expected: 201 Created with book object including UUID
```

**List books (cursor pagination):**
```bash
# First page
curl "http://localhost:8000/api/v1/books?limit=10" \
  -H "Authorization: Bearer $TOKEN"
# Expected: {"items": [...], "next_cursor": "eyJ...", "has_more": true}

# Next page (use next_cursor from previous response)
curl "http://localhost:8000/api/v1/books?limit=10&cursor=<next_cursor>" \
  -H "Authorization: Bearer $TOKEN"
```

**Get single book:**
```bash
curl "http://localhost:8000/api/v1/books/{book_id}" \
  -H "Authorization: Bearer $TOKEN"
# Expected: Single book object or 404
```

### Level 4: Update & Delete

**Update book:**
```bash
curl -X PUT "http://localhost:8000/api/v1/books/{book_id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code - Updated",
    "author": "Robert C. Martin"
  }'
# Expected: 200 OK with updated book
```

**Delete book:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/books/{book_id}" \
  -H "Authorization: Bearer $TOKEN"
# Expected: 204 No Content
```

### Level 6: Filtering & Advanced Pagination

**Filter by author:**
```bash
curl "http://localhost:8000/api/v1/books?author=Robert%20Martin&limit=10" \
  -H "Authorization: Bearer $TOKEN"
# Expected: Only books by Robert Martin
```

**Cursor pagination deep page:**
```bash
# Keep following next_cursor to test pagination stability
curl "http://localhost:8000/api/v1/books?cursor=<deep_cursor>&limit=10" \
  -H "Authorization: Bearer $TOKEN"
# Performance should remain <50ms even at page 1000+
```

### Level 7: Error Handling

**401 Unauthorized:**
```bash
curl http://localhost:8000/api/v1/books
# Expected: {"error": "Not authenticated", "status_code": 401}
```

**404 Not Found:**
```bash
curl "http://localhost:8000/api/v1/books/00000000-0000-0000-0000-000000000000" \
  -H "Authorization: Bearer $TOKEN"
# Expected: {"error": "Not Found", "detail": "...", "status_code": 404}
```

**422 Validation Error:**
```bash
curl -X POST http://localhost:8000/api/v1/books \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": ""}'
# Expected: {"error": "Validation Error", "status_code": 422}
```

### Level 8: Performance Verification

**Check index usage (inside PostgreSQL):**
```bash
# Enter PostgreSQL container
docker exec -it books_db psql -U bookuser -d booksdb

# Verify cursor pagination uses index
EXPLAIN ANALYZE SELECT * FROM books
ORDER BY created_at DESC, id ASC
LIMIT 10;
# Should show: "Index Scan using idx_books_created_at" (NOT Seq Scan)

# Verify filtered pagination uses composite index
EXPLAIN ANALYZE SELECT * FROM books
WHERE author = 'Robert Martin'
ORDER BY created_at DESC, id ASC
LIMIT 10;
# Should show: "Index Scan using idx_books_author_created"

# Exit
\q
```

---

## Database Seeding (Optional)

To test with sample data, create a migration:

```bash
# Inside app container
docker exec -it books_api bash

# Create seed migration
alembic revision -m "Seed sample books"

# Edit the migration file in alembic/versions/
# Add sample data generation code (see plan for example)

# Apply migration
alembic upgrade head
```

---

## Project Structure

```
backend-test-desent/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Settings
│   ├── dependencies.py            # DI setup
│   ├── api/v1/routers/            # API endpoints
│   │   ├── health.py              # Level 1-2
│   │   ├── auth.py                # Level 5
│   │   └── books.py               # Level 3-4, 6
│   ├── services/                  # Business logic
│   │   └── book_service.py
│   ├── repositories/              # Data access
│   │   └── book_repository.py
│   ├── models/                    # SQLAlchemy ORM
│   │   └── book.py
│   ├── schemas/                   # Pydantic schemas
│   │   ├── book.py
│   │   └── auth.py
│   ├── core/                      # Core utilities
│   │   ├── database.py            # Async session
│   │   ├── security.py            # JWT + bcrypt
│   │   └── pagination.py          # Cursor logic
│   └── middleware/
│       └── error_handler.py       # Level 7
├── alembic/                       # Database migrations
├── docker/                        # Docker files
├── docker-compose.yml
└── pyproject.toml
```

---

## Architecture Highlights

### Layered Architecture
- **Router** → **Service** → **Repository** → **Database**
- Clean separation of concerns
- Easy testing and maintenance

### Cursor Pagination
- **Performance**: O(log n) vs O(n) for OFFSET
- **Stable**: Works with concurrent writes
- **Scalable**: <50ms even at page 10,000+

**Implementation:**
```python
# Instead of: OFFSET 100000 LIMIT 10 (slow!)
# We use: WHERE created_at < 'cursor_time' ORDER BY created_at DESC LIMIT 10 (fast!)
```

### Database Indexes

**Critical indexes for performance:**
```sql
-- Cursor pagination
CREATE INDEX idx_books_created_at ON books(created_at DESC);

-- Author filtering
CREATE INDEX idx_books_author ON books(author);

-- Filtered pagination (composite)
CREATE INDEX idx_books_author_created ON books(author, created_at DESC);
```

---

## Development

### Run Migrations

```bash
# Generate migration from model changes
docker exec -it books_api alembic revision --autogenerate -m "Description"

# Apply migrations
docker exec -it books_api alembic upgrade head

# Rollback last migration
docker exec -it books_api alembic downgrade -1
```

### View Logs

```bash
# App logs
docker logs -f books_api

# PostgreSQL logs
docker logs -f books_db
```

### Stop Services

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (wipes database)
docker-compose down -v
```

---

## Testing Checklist

- [ ] **Level 1**: Ping returns pong
- [ ] **Level 2**: Echo returns request body
- [ ] **Level 3**: CRUD operations work (create, list, get)
- [ ] **Level 4**: Update and delete work
- [ ] **Level 5**: JWT auth protects all `/books` endpoints
- [ ] **Level 6**: Cursor pagination & author filtering work
- [ ] **Level 7**: Error responses are standardized (401, 404, 422, 500)
- [ ] **Level 8**: Query performance <50ms (verify with `EXPLAIN ANALYZE`)
- [ ] Swagger UI accessible at `/docs`
- [ ] All indexes created (check with `\d books` in psql)

---

## Performance Tips

1. **Always use cursor pagination** for large datasets
2. **Verify indexes with EXPLAIN ANALYZE** before deploying
3. **Monitor connection pool** usage (default: 20 connections)
4. **Adjust pool_size** in [app/config.py](app/config.py) based on load

---

## Troubleshooting

**"Connection refused" errors:**
```bash
# Wait for PostgreSQL healthcheck to pass
docker-compose logs db | grep "database system is ready"
```

**Migration errors:**
```bash
# Check current migration state
docker exec -it books_api alembic current

# Reset migrations (DESTRUCTIVE - wipes data)
docker-compose down -v
docker-compose up --build
```

**Import errors:**
```bash
# Rebuild container
docker-compose up --build
```

---

## Tech Stack

- **FastAPI** 0.109+ - Modern async web framework
- **SQLAlchemy** 2.0+ - Async ORM
- **PostgreSQL** 16 - Relational database
- **asyncpg** - Fast async PostgreSQL driver
- **Alembic** - Database migrations
- **Pydantic** v2 - Data validation
- **python-jose** - JWT implementation
- **passlib** - Password hashing

---

## License

MIT

---

## Next Steps

- Add automated tests (pytest + httpx)
- Implement response time middleware
- Add logging and monitoring
- Deploy to Render/Railway/Fly.io
- Load test with 1M rows

**Happy coding!** 🚀
