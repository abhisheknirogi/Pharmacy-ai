## Developer Run Instructions

TL;DR — Quick checklist
- Create Python venv → install deps → configure `.env` → run migrations → seed DB → start backend → start frontend → run tests.

**Prerequisites**
- Python 3.10+ (3.11 recommended)
- Node.js 18+ and npm
- Git
- Optional: Docker & Docker Compose (for full-stack runs)

**Important repo paths to know**
- Backend app entry: `backend/app/main.py`
- Backend config: `backend/app/config.py` (reads `.env`)
- Alembic: `alembic.ini`, `alembic/env.py`
- Seed script: `scripts/seed_db.py`
- Frontend: `frontend/` (`package.json`, `next.config.js`)
- Production compose: `docker-compose.prod.yml`
- Dev compose: `docker-compose.yml`


=== Local Dev (PowerShell on Windows) ===
Run these steps from the repository root.

1) Create & activate virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
If activation fails see Troubleshooting -> ExecutionPolicy.

2) Install Python dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

3) Install frontend dependencies
```powershell
cd frontend
npm install
cd ..
```

4) Create `.env` (repo root or ensure process CWD contains `.env`)
- Copy or create `.env` and add minimal values:
```
DATABASE_URL=sqlite:///./pharmacy.db
SECRET_KEY=change-me
DEBUG=True
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```
(Production values are in `.env.production` in docs and `docker-compose.prod.yml`.)

5) Apply DB migrations (Alembic)
```powershell
alembic upgrade head
```
If Alembic not available: `pip install alembic` first.

6) Seed the database (creates demo user + sample data)
```powershell
python scripts/seed_db.py
```

7) Run backend (FastAPI)
Open a terminal (with venv activated) and run:
```powershell
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Alternative run (from repo root):
```powershell
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

8) Run frontend (Next.js)
Open a second terminal:
```powershell
cd frontend
npm run dev
```

9) Visit the app
- Frontend: http://localhost:3000
- Backend health: http://localhost:8000/health
- API docs (if enabled): http://localhost:8000/docs


=== Run with Docker Compose ===
(Docker Desktop recommended on Windows)

1) Build and start development stack
```powershell
docker-compose up --build
```
2) Stop and remove
```powershell
docker-compose down
```

3) Production compose (careful: requires secrets and resources)
```powershell
docker-compose -f docker-compose.prod.yml up -d
```
Check `docker-compose.prod.yml` for Postgres, Redis, Nginx, Prometheus and set environment variables in `.env` accordingly.


=== Running tests & linters ===
From repo root (venv active):
```powershell
pytest tests/ -v
# or via Makefile targets if present
make test
```

Lint/format (if configured):
```powershell
make lint
make format
```


=== Troubleshooting (common issues) ===
- PowerShell activation blocked:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
- Port conflict: common ports are `8000` and `3000` — find process using port:
```powershell
netstat -ano | findstr ":8000"
Get-Process -Id <PID>
```
- SQLite DB locked: stop processes using `pharmacy.db` or delete to reset:
```powershell
del pharmacy.db
# then re-run migrations and seed
alembic upgrade head
python scripts/seed_db.py
```
- Alembic errors: ensure `alembic` is installed and `alembic.ini` points to correct DB URL. Run migrations from repo root so Alembic finds `alembic/env.py`.
- Docker permission/volume errors: check Docker Desktop settings and the volume mounts in the compose file.


=== Useful Make targets (if Makefile exists) ===
- `make install` — install Python deps
- `make run` — run backend
- `make frontend-install` — `cd frontend && npm install`
- `make frontend-dev` — `cd frontend && npm run dev`
- `make db-migrate` — `alembic upgrade head`
- `make db-seed` — run `scripts/seed_db.py`
- `make test` — run pytest


=== Notes & references ===
- Backend settings loader reads `.env` (see `backend/app/config.py`). Place `.env` in the working directory used to start the backend.
- Seed script: `scripts/seed_db.py` (creates demo user `demo@pharmacy.com / demo123456`).
- Alembic config: `alembic.ini`, migrations folder `alembic/`.


If you want, I can also:
- create a `.env.example` file in the repo with minimal values,
- or attempt to run the dev stack locally from this environment (I tried to configure a Python interpreter earlier but the environment selection wasn't completed). 

---
