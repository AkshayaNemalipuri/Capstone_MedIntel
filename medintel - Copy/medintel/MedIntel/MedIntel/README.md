# MedIntel

MedIntel is a healthcare platform that combines secure medical record management, AI-based risk prediction, and role-based access for patients, doctors, and admins.

## Team database guide

See [DATABASE_SETUP.md](DATABASE_SETUP.md) for the shared Supabase PostgreSQL setup, migration commands, authentication flow, and table ownership rules.

## Modules

- Module 1: Authentication & User Management
- Module 2: Patient Health Records
- Module 3: AI Prediction Module
- Module 4: Dashboard & Analytics
- Module 5: Doctor/Admin Panel

## Stack

- Frontend: React + Vite
- Backend: FastAPI
- Database: PostgreSQL
- Auth: Clerk
- AI: Python + scikit-learn

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Before starting the backend, create a Supabase project. Supabase provides a hosted PostgreSQL database, so the whole team can use one shared database. In Supabase Dashboard, open **Connect**, choose the **Session pooler**, and copy its URI into `backend/.env`:

```env
DATABASE_URL=postgresql://postgres.<project-ref>:<password>@<region>.pooler.supabase.com:5432/postgres?sslmode=require
JWT_SECRET=<long-random-secret>
```

Run the Alembic migration before starting the backend. It creates the Module 1 `users` and `password_reset_tokens` tables in Supabase. The same database URL can be shared with the team through a private environment-variable manager. Do not commit `.env` or database passwords. Other modules should reference `users.id` and create their own tables rather than changing the authentication tables.

Supabase setup checklist:

1. Create one Supabase project for the team.
2. Add `DATABASE_URL` and `JWT_SECRET` to `backend/.env` on each developer machine.
3. Run the backend once to create the initial auth table.
4. Apply the schema with `python -m alembic upgrade head`.
5. Use tracked migration files when adding tables for other modules.
6. Never put the Supabase database password in GitHub or frontend code.

Module 1 endpoints:

- `POST /api/auth/register` creates a user and returns a JWT session
- `POST /api/auth/login` validates credentials and returns a JWT session
- `GET /api/auth/me` reads the authenticated profile
- `PATCH /api/auth/me` updates the authenticated profile name
- `POST /api/auth/forgot-password` starts the reset request flow
- `GET /api/auth/dashboard` verifies the current JWT and role

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend calls `http://localhost:8000` by default. Use `VITE_API_URL` in `frontend/.env` when the team shares a deployed backend.

## Team workflow

- Member 1: Authentication & User Management
- Member 2: Patient Health Records
- Member 3: AI Prediction Module
- Member 4: Dashboard & Analytics
- Member 5: Doctor/Admin Panel
