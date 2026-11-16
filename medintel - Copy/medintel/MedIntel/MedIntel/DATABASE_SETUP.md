# Shared Database Setup

This project uses **Supabase**, which provides a hosted PostgreSQL database. The team should use one shared Supabase project instead of creating separate databases on individual laptops.

## What to share with the team

Share these items through a private channel, not in GitHub:

- Supabase project name
- Supabase dashboard link
- PostgreSQL connection string
- Database username
- Database password
- Project responsibilities

Never commit the real connection string or password. The local file `backend/.env` is ignored by Git.

## Backend setup

1. Install PostgreSQL dependencies from `backend/requirements.txt`.
2. Copy `backend/.env.example` to `backend/.env`.
3. Put the shared Supabase PostgreSQL URI in `backend/.env`.
4. If the password contains special characters, URL-encode them. For example, `@` becomes `%40`.
5. Apply the schema:

```powershell
cd backend
python -m alembic upgrade head
```

6. Start the API:

```powershell
uvicorn app.main:app --reload --port 8000
```

## Database ownership

The database is centralized, but tables have owners:

| Owner | Tables or responsibility |
| --- | --- |
| Module 1 | `users`, `password_reset_tokens`, authentication and role rules |
| Module 2 | Patient records, uploaded file metadata, and health documents |
| Module 3 | AI predictions, model outputs, and risk scores |
| Module 4 | Analytics queries and dashboard data |
| Module 5 | Doctor/admin workflow data and integration testing |

Other modules should reference `users.id`. They should not modify the authentication tables directly.

## Authentication flow

- Registration creates a patient account in `users`.
- Login checks the email and password against `users`.
- Passwords are stored as hashes, never plain text.
- Successful login returns a JWT session token.
- Protected API requests send the token as `Authorization: Bearer <token>`.
- The backend gets the role from the database; login does not ask the user to choose a role.
- Doctor and admin access must be assigned by an authorized admin.

## Useful API endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `PATCH /api/auth/me`
- `POST /api/auth/forgot-password`
- `POST /api/auth/reset-password`
- `PATCH /api/auth/{user_id}/role` for admins only

## Team workflow

Create schema changes as Alembic migrations. Do not edit the shared database manually for changes that need to be reproduced by teammates.

```powershell
python -m alembic revision -m "describe your change"
python -m alembic upgrade head
```

Before pushing code, verify that no secrets are staged:

```powershell
git status --short --ignored
git check-ignore backend/.env
```
