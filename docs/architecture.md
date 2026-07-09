# Architecture

## Current state

This project is two independently scaffolded pieces that are not yet connected:

- **`backend/`** — a stock `django-admin startproject` (Django 6.0, project name `config`) plus one app, `agent_api`, generated via `startapp` and not yet registered in `INSTALLED_APPS` (`backend/config/settings.py`). `agent_api/models.py` and `agent_api/views.py` are empty. `backend/config/urls.py` only exposes `/admin/`.
- **`frontend/`** — a stock Vite + React + TypeScript template (`npm create vite`). No API client, no fetch/axios calls, no dev-server proxy to the backend (`frontend/vite.config.ts` has none configured).

Local dev database is SQLite (`backend/db.sqlite3`, created on first `migrate`) — fine for now, will need revisiting before any shared/deployed environment.

## Next decisions

These aren't decided yet — record the answer here once they are:

- What does `agent_api` actually do? (What's the "agent" — LLM-backed task agent, task queue, something else?)
- REST framework choice for the backend (plain Django views, Django REST Framework, Ninja, etc.)
- How the frontend talks to the backend in dev (Vite proxy vs. CORS vs. same-origin) and in whatever deployed form this takes
- Auth model, if any beyond Django admin

## Why docs live here

Root-level `docs/` holds anything that describes how the whole system fits together (this file, setup, API contracts) rather than being split per-stack, since the two stacks need a shared source of truth for how they integrate. Stack-local docs (e.g. `frontend/README.md`) are fine for notes that only matter inside that stack.
