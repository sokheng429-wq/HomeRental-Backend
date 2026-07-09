# Home Rental API (FastAPI + Neon Postgres)

Backend for the Home Rental app. Provides auth, listings, and the rental
chat bot (rule-based, queries real listings — see `app/chatbot.py`).

## 1. Create a Neon Postgres database

1. Sign up / log in at https://neon.tech and create a project (this also
   creates a default database, e.g. `home_rental` or `neondb`).
2. On the project dashboard, copy the **connection string** (use the
   "Pooled connection" string, since serverless functions and local dev
   servers both benefit from it).
3. It looks like:
   `postgresql://user:password@ep-xxxx-pooler.region.aws.neon.tech/home_rental?sslmode=require`
4. Change the scheme from `postgresql://` to `postgresql+psycopg2://` so
   SQLAlchemy uses the right driver, keep `?sslmode=require`.

No local database server or Docker needed — Neon is fully hosted.

## 2. Set up the Python environment

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # paste your Neon connection string into DATABASE_URL
```

## 3. Seed demo data (optional but recommended)

Creates a demo landlord account and the 5 sample listings from the original
prototype so the Home screen isn't empty:

```bash
python -m app.seed
```

Demo login: `demo@homerental.app` / `password123`

## 4. Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

- API root: http://localhost:8000
- Interactive docs (Swagger): http://localhost:8000/docs

Tables are created automatically on startup (`Base.metadata.create_all`).
For a real production setup you'd want Alembic migrations instead — this is
kept simple for local development.

## Troubleshooting

- **"password authentication failed"** — your `DATABASE_URL` credentials
  don't match Neon. Re-copy the connection string from the Neon dashboard
  (it may have rotated if you reset the password).
- **"SSL connection is required"** — make sure `?sslmode=require` is at the
  end of `DATABASE_URL`; Neon rejects non-SSL connections.
- **"could not connect to server" / timeouts** — check the endpoint isn't
  paused (Neon's free tier auto-suspends idle projects; it wakes on the
  next connection, which can take a few seconds) and that your network
  allows outbound connections on port 5432.
- **"database does not exist"** — use the database name shown on your Neon
  dashboard (defaults to `neondb` unless you renamed it), or create one
  with `CREATE DATABASE home_rental;` via the Neon SQL editor.

## Endpoints

| Method | Path                | Auth | Description                          |
|--------|---------------------|------|---------------------------------------|
| POST   | /auth/register      | no   | Create account, returns JWT           |
| POST   | /auth/login         | no   | Login, returns JWT                    |
| GET    | /auth/me            | yes  | Current user info                     |
| PUT    | /auth/me            | yes  | Update profile fields                 |
| GET    | /listings           | no   | List/search listings (`?search=&type=`) |
| GET    | /listings/{id}      | no   | Single listing                        |
| POST   | /listings           | yes  | Create a listing                      |
| DELETE | /listings/{id}      | yes  | Delete your own listing               |
| GET    | /chat/history       | yes  | This user's chat history (seeds a welcome message) |
| POST   | /chat/message       | yes  | Send a message, get the bot's reply   |

Auth uses a `Bearer <token>` header. The frontend (`src/api.js`) handles
this automatically once you're logged in.
"# HomeRental-Backend" 
