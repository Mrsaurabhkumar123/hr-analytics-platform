# Pulse — HR Analytics & Employee Intelligence Platform

A working full-stack HR analytics platform: JWT-authenticated Flask API backed by MySQL,
a scikit-learn attrition-risk model trained on a realistic synthetic workforce dataset,
and a React + TypeScript dashboard frontend.

This is **one buildable, functional slice** of the much larger enterprise spec it was
built from — see [Scope & what's built](#scope--whats-built) below for exactly what's
real vs. what's roadmap.

---

## Quick start (Docker)

```bash
cp .env.example .env        # edit secrets/passwords before any real deployment
docker compose up --build
```

This starts three containers:

| Service  | URL                         | Notes                                             |
|----------|------------------------------|----------------------------------------------------|
| mysql    | localhost:3306                | Persists to a named volume                         |
| backend  | http://localhost:5000/api     | Auto-seeds demo data + trains the ML model on boot |
| frontend | http://localhost:5173         | React SPA served by nginx                          |

First boot takes ~1–2 minutes: MySQL initializes, the backend waits for it, seeds ~420
synthetic employees across 8 departments, then trains the attrition model before starting
Gunicorn. Watch logs with `docker compose logs -f backend`.

Once it's up, open **http://localhost:5173** and sign in with one of the demo accounts
below (also shown on the login screen).

### Demo logins

| Role               | Email                          | Password        |
|--------------------|----------------------------------|------------------|
| Super Admin        | admin@hranalytics.io             | Admin@12345      |
| HR Admin           | hr.admin@hranalytics.io          | HrAdmin@123      |
| HR Manager         | hr.manager@hranalytics.io        | HrManager@123    |
| Department Manager | dept.manager@hranalytics.io      | DeptMgr@123      |
| Team Lead          | team.lead@hranalytics.io         | TeamLead@123     |
| Employee           | employee@hranalytics.io          | Employee@123     |
| Auditor            | auditor@hranalytics.io           | Auditor@123      |

Change every one of these before this ever touches real data.

---

## Running without Docker

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # point DB_HOST at a MySQL instance you have running locally
python -m app.seed              # generate demo data
python -m app.ml.train_model    # train the attrition-risk model
python wsgi.py                  # dev server on :5000
```

**Frontend**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev   # :5173
```

---

## Scope & what's built

The original brief specified a huge platform: 10+ dashboards, resume parsing, an org
chart, an AI chat assistant, 2FA, audit logs, workforce forecasting, and more. Generating
all of that as genuinely functional code in one pass isn't realistic — it would mean
either an enormous low-quality dump or an honest, working core. This build is the latter.

**Built and functional:**
- JWT auth (access + refresh tokens), role-based access control for 7 roles, admin user
  provisioning, password change
- MySQL schema via SQLAlchemy models (Employee, Department, User, Attendance, Leave,
  Performance) — see `database/schema.sql` for the reference DDL
- Realistic synthetic dataset generator (`backend/app/seed.py`) — attrition outcomes are
  correlated with salary hikes, promotions, attendance, and satisfaction, not random noise
- **Executive Dashboard** — KPIs, hiring trend, headcount by department
- **Employee Directory** — search, filter by department/status, sortable columns,
  pagination, CSV export, role-gated salary visibility
- **AI Employee Risk Prediction** — a real Random Forest classifier
  (`backend/app/ml/train_model.py`) trained on 13 engineered features, with accuracy /
  precision / recall / F1 / ROC-AUC / feature importance exposed via API, and
  per-employee risk score + human-readable reasons + suggested actions
  (`backend/app/ml/predict.py`)
- Rate-limit-ready structure, input validation, CORS lockdown, password hashing, CSV
  export, error handling, structured logging
- Docker Compose for the full stack

**Sidebar items shown as "Coming soon"** (not built, not faked): Departments, Salary,
Leave, Training, Recruitment, Performance dashboards. The database models and some API
groundwork for several of these already exist (`AttendanceRecord`, `LeaveRecord`,
`PerformanceReview`, `/api/departments/:id/stats`) — they just don't have frontend pages
yet. Ask for any of these specifically and they can be built the same way as the three
above.

**Not attempted in this pass** (would need real integrations, not just UI): 2FA,
email verification, resume parsing, AI chat assistant, org chart, workforce forecasting,
document management, audit logs, scheduled report generation, dashboard personalization.
The `User` model already has `two_factor_enabled` / `two_factor_secret` columns reserved
for when 2FA is added.

---

## Project structure

```
backend/                  Flask API
  app/
    models/                SQLAlchemy models (Employee, Department, User, ...)
    routes/                Blueprints: auth, employees, departments, dashboard, attrition
    ml/                    train_model.py, predict.py, artifacts/ (generated)
    utils/                 RBAC decorator, validators
    seed.py                Synthetic dataset generator
  wsgi.py                  Production entrypoint (gunicorn)
  scripts/entrypoint.sh    Container boot sequence (wait for DB → seed → train → serve)

frontend/                 React + TypeScript + Vite + Tailwind
  src/
    pages/                 Login, ExecutiveDashboard, EmployeeDirectory, AttritionRisk
    components/            Sidebar, KpiCard, RiskBadge, shared state views
    api/client.ts           Axios client with JWT refresh interceptor
    context/AuthContext.tsx

database/schema.sql        Reference DDL (actual schema is managed by SQLAlchemy)
docker-compose.yml          MySQL + backend + frontend orchestration
```

The original brief also named top-level `datasets/`, `machine_learning/`, `dashboard/`,
`reports/`, `analytics/`, `tests/`, `config/`, `docs/`, `assets/` folders. Rather than
create empty directories to match the list, their actual content lives where it
functionally belongs above (ML in `backend/app/ml/`, config in `backend/app/config.py`
and `.env` files, etc.) — happy to split any of these out into separate top-level folders
if that layout matters for your team's conventions.

---

## Extending this

- **New dashboard page**: add a Flask blueprint under `backend/app/routes/`, register it
  in `backend/app/__init__.py`, then add a React page + sidebar entry.
- **Retrain the model** after seeding more data: `python -m app.ml.train_model` (or
  `docker compose exec backend python -m app.ml.train_model`).
- **Reset demo data**: `python -m app.seed --reset`.
- **Add a role's permissions**: extend `Role` in `backend/app/models/user.py` and gate
  routes with the `@roles_required(...)` decorator.
