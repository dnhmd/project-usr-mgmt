## usr-mgmt

A production-ready backend engineered to demonstrate scalable patterns: asynchronous database operations with SQLAlchemy, secure JWT refresh token rotation, strict role-based access control, and comprehensive integration test suites. It can perform as the basic for most applications, a

### Why I built this?

This project serves two core purposes:

- To implement and master production-grade backend patterns (like async SQLAlchemy, RBAC, and JWT token rotation) that go beyond basic CRUD tutorials.

- To create a highly scalable, "plug-and-play" starter template. Because almost every modern application requires user management and security boundaries, this repository acts as a robust boilerplate that allows me to bootstrap future projects instantly without sacrificing production standards.

### Tech Stack

-   ****Python 3.10**** + ****FastAPI****
-   ****PostgreSQL**** via ****Docker****
-   ****SQLAlchemy**** (async) + ****Alembic**** migrations
-   ****JWT**** authentication (access + refresh tokens)
-   ****bcrypt**** password hashing
-   ****slowapi**** rate limiting
-   ****pytest**** + ****httpx**** integration tests

### Prerequisites

-   Python 3.10+
-   Docker + Docker Compose
-   Git

### Setup & Run

bash

\# 1. Clone and enter  
git clone https://github.com/dnhmd/project-usr-mgmt.git
cd usr-mgmt  
  
\# 2. Create and activate virtual environment  
python3 -m venv .venv  
source .venv/bin/activate  
  
\# 3. Install dependencies  
pip install -e ".\[dev\]"  
  
\# 4. Configure environment  
cp .env.example .env  
\# Edit .env with your values  
  
\# 5. Start Postgres  
docker compose up -d  
  
\# 6. Run migrations  
alembic upgrade head  
  
\# 7. Seed roles  
docker exec -it postgres\_slim psql -U myuser -d usr\_mgmt -c "INSERT INTO roles (name) VALUES ('user'), ('admin');"  
  
\# 8. Start server  
uvicorn app.main:app --reload

### Running Tests

bash

```
pytest tests/ -v
```

31 integration tests covering auth flows, authorization rules, validation, and edge cases.

### Environment Variables

See `.env.example` for all required variables:

| Variable                            | Description                  | Default                   |
| ----------------------------------- | ---------------------------- | ------------------------- |
| DATABASE_URL                        | PostgreSQL connection string | —                         |
| SECRET_KEY                          | JWT signing key              | —                         |
| ACCESS_TOKEN_EXPIRE_MINUTES         | Access token TTL             | 30                        |
| PASSWORD_RESET_TOKEN_EXPIRE_MINUTES | Reset token TTL              | 10                        |
| ALGORITHM                           | JWT algorithm                | HS256                     |
| ENVIRONMENT                         | App environment              | development               |
| DEBUG                               | Enable debug mode            | False                     |
| ALLOWED_ORIGINS                     | CORS allowed origins         | ["http://localhost:3000"] |

### API Endpoints

#### Auth — `/api/v1/auth`

| Method | Endpoint         | Auth | Description               |
| ------ | ---------------- | ---- | ------------------------- |
| POST   | /register        | None | Register new user         |
| POST   | /login           | None | Login                     |
| POST   | /refresh         | None | Refresh access token      |
| POST   | /forgot-password | None | Request password reset    |
| POST   | /reset-password  | None | Reset password with token |

#### Users — `/api/v1/users`

| Method | Endpoint            | Auth               | Description                       |
| ------ | ------------------- | ------------------ | --------------------------------- |
| GET    | /                   | Admin              | List users (paginated + filtered) |
| GET    | /{user_id}          | User (own) / Admin | Get user                          |
| PATCH  | /{user_id}          | User (own) / Admin | Update name/email                 |
| PATCH  | /{user_id}/password | User (own) only    | Change password                   |
| PATCH  | /{user_id}/role     | Admin              | Change role                       |
| DELETE | /{user_id}          | Admin              | Soft delete user                  |

### Notes

-   Passwords are hashed with bcrypt — never stored in plaintext
-   Refresh tokens are single-use and rotate on every refresh
-   Rate limiting is applied on all auth endpoints
-   All errors return a consistent JSON structure with a `request_id` for tracing
-   Deleted users are soft-deleted (`is_active=False`), not removed from the database