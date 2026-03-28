# QShift

QShift is a staff scheduling app. It generates weekly shift proposals for employees while respecting availability
windows and staffing requirements.

The backend is split into two APIs:

- `core_api`: auth, persistence, job orchestration, callback handling
- `schedule_generator_api`: internal service responsible for schedule generation

The frontend consumes only the `core_api`.

## Architecture

```mermaid
flowchart TB
    subgraph CL["Client Layer"]
        F[Frontend<br/>React + Vite]
    end

    subgraph AL["Application Layer"]
        C[core_api<br/>FastAPI]
        G[schedule_generator_api<br/>FastAPI]
    end

    subgraph DL["Data Layer"]
        DB[(PostgreSQL)]
    end

    F -->|HTTP| C
    C -->|dispatch generation job| G
    G -->|authenticated callback with result| C
    C -->|read/write| DB
```

Local ports:

- `frontend`: `5173`
- `core_api`: `8000`
- `schedule_generator_api`: `8001`

## Initial Setup

Requirements:

- Python `3.12+`
- Node.js + npm
- PostgreSQL

Backend:

```bash
cd backend
cp .env.example .env
../.venv/bin/pip install -r requirements-dev.txt
./scripts/init_db.sh
./scripts/migrate_db.sh
```

`init_db.sh` creates the local PostgreSQL user/database expected by the current dev setup. Keep `backend/.env` aligned
with those values.

Minimum `backend/.env` values:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/qshift
SECRET_KEY=CHANGE_ME
SCHEDULE_GENERATOR_BASE_URL=http://localhost:8001
CORE_API_BASE_URL=http://localhost:8000
SCHEDULE_CALLBACK_SECRET=CHANGE_ME
```

Generate secure secrets with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Frontend:

```bash
cd frontend
npm install
```

`frontend/.env`:

```env
VITE_BASE_URL=http://localhost:8000/api/v1
```

## Run

Start the main API:

```bash
cd backend
./scripts/run.sh
```

Start the schedule generator API:

```bash
cd backend
./scripts/run_generator.sh
```

Start the frontend:

```bash
cd frontend
npm run dev
```

## Optimization Model

The schedule generator uses Google OR-Tools CP-SAT.

Hard constraints:

- an employee can only be assigned to shifts fully covered by their availability
- an employee cannot be assigned to overlapping shifts on the same day

Optimization is done in stages:

1. Minimize deviation from required staffing per shift.
2. Keep workload balanced across employees by minimizing deviation from the average target workload.
3. Reduce fragmented days by minimizing cases where the same employee receives multiple shifts in a single day.

In short: feasibility comes first, coverage quality comes next, and fairness/shift concentration are refined after that.

## Tests

Backend:

```bash
cd backend
./scripts/test.sh
```

Frontend production build:

```bash
cd frontend
npm run build
```
