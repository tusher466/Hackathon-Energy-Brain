# Deploy Energy Brain to Render – Step by Step (Market-Ready Updated)

Repo already pushed to https://github.com/tusher466/Hackathon-Energy-Brain with `render.yaml` blueprint that now has `branch: main` and `autoDeploy: true` on all 3 services.

## Option A – Blueprint (Recommended, 3 services auto - market ready)

1. Go to https://dashboard.render.com/ → **New +** → **Blueprint**
2. Connect GitHub account and select repo `tusher466/Hackathon-Energy-Brain`
3. Render detects `render.yaml` with 3 services (now market-ready with branch + autoDeploy):
   - `energy-brain-backend` (Docker, single URL serves full-stack frontend+backend)
   - `energy-brain-frontend` (Static, optional)
   - `energy-brain-landing` (Static)
4. Click **Apply**. Render will:
   - Build backend Docker multi-stage: `node:20-alpine` builds frontend with `VITE_API_URL=""` same-origin, then `python:3.11-slim` installs deps, copies `frontend/dist` → `./frontend/dist` + `./static`, runs `uvicorn` with 2 workers and `HEALTHCHECK curl /health`
   - Health check `/health` must return 200
   - Build frontend static: `npm install && npm run build`
   - Publish `frontend/dist` with SPA rewrite `/* → /index.html`
5. After first deploy, backend URL will be `https://energy-brain-backend.onrender.com` – this single URL now serves BOTH API AND frontend (because root Dockerfile bundles frontend). So `https://energy-brain-backend.onrender.com/` loads control room, `/api/v1/...` still API, `/docs` API docs, `/landing` landing page.
   - If you use separate frontend static service, its URL e.g. `https://energy-brain-frontend.onrender.com` will call backend via `VITE_API_URL=https://energy-brain-backend.onrender.com` set in `render.yaml:39`
   - If frontend built before backend URL known, update env var `VITE_API_URL` in frontend service to backend URL and **Manual Deploy → Clear build cache & Deploy**
6. CORS is now market-ready: `render.yaml:14` sets `CORS_ORIGINS` to include all Render domains plus `*` → backend `app/core/config.py:21` defaults allow all `*`, and `app/main.py:36` correctly sets `allow_credentials=False` when `*` present. So frontend static can call backend even with changing URLs.
7. Optional secrets: add `NREL_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `ELECTRICITYMAPS_API_KEY` in backend env dashboard (sync: false). App works without them – synthetic fallback offline-first.
8. **Auto-Update**: All services now have `branch: main` and `autoDeploy: true` in `render.yaml:7,32,47`. Every `git push origin main` (like `e3539e8 market-ready` and this new deploy fix) auto-triggers redeploy. Verify in Dashboard → Service → Events → Deploy triggered via git push. If you created services manually (not Blueprint), go to Service → Settings → Build & Deploy → Auto-Deploy ON, Branch main, DockerfilePath ./Dockerfile, Context .

## Option B – Manual 2 Services

### Backend Web Service
- Runtime: Python 3.11
- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health Check: `/health`
- Env Vars:
  - `PYTHON_VERSION=3.11.0`
  - `CORS_ORIGINS=https://energy-brain-frontend.onrender.com`

### Frontend Static Site
- Root Directory: `frontend`
- Build Command: `npm install && npm run build`
- Publish Directory: `dist`
- Env Var: `VITE_API_URL=https://<your-backend>.onrender.com`
- Add Rewrite Rule: Source `/*` Destination `/index.html` Action `Rewrite` (or use render.yaml which already does).

## Verification After Deploy

- Backend: `https://your-backend.onrender.com/health` → `{"status":"ok"}`
- Backend Docs: `https://your-backend.onrender.com/docs`
- Frontend: opens control room, fetches regions – check region switch BD/DE/US
- Ledger: after VPP dispatch, summary updates

## Local Run Still Works

```bash
# backend
cd backend && uvicorn app.main:app --reload --port 8000
# frontend
cd frontend && npm run dev
```

## Notes for Render Free Tier

- Free tier sleeps after 15 min idle – first request may take 30s cold start
- SQLite persists in container ephemeral disk – ledger resets on redeploy; for production use Postgres – update `DATABASE_URL` env to Render Postgres internal URL
- Frontend static is free, backend web service free tier 750 hours/month

## Architecture on Render

```
Browser → https://frontend.onrender.com (static SPA)
         → fetches https://backend.onrender.com/api/v1/*
         → backend renders OpenAPI docs
         → SQLite ledger (ephemeral) → for Postgres, add Render Postgres
```

Pushing new commits to `main` auto-triggers redeploy if auto-deploy enabled.

## Troubleshooting – Your Screenshot Error Fixed

**Error log you saw:**
```
#1 [internal] load build definition from Dockerfile
...
error: failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory
```

**Root cause:** You created a Web Service manually with **Environment: Docker** pointing to repository root. Render then looks for `Dockerfile` in root, but we only had `backend/Dockerfile` and `frontend/Dockerfile`. So it failed.

**Fix applied (commit 5ed6fad):**
1. Added root `Dockerfile` that builds backend (python:3.11-slim, installs opencv deps, copies `backend/`, runs `uvicorn` with `$PORT`):
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
   COPY backend/requirements.txt ./
   RUN pip install --no-cache-dir -r requirements.txt
   COPY backend/ ./
   EXPOSE 8000
   CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
   ```
2. Switched `render.yaml` backend from `env: python` to `env: docker` with:
   ```yaml
   dockerfilePath: ./Dockerfile
   dockerContext: .
   ```
3. Added `.dockerignore`
4. Pushed to `main` → Render auto-redeploys. Manual Docker service now finds root Dockerfile and builds successfully.

**If still failing:**
- Go to Render Dashboard → your service → **Manual Deploy → Clear build cache & Deploy**
- Ensure service Type is **Docker** for backend (or use Blueprint which creates correct type). For Blueprint: **New → Blueprint → select repo** – it will read `render.yaml` and create both services correctly.
- Frontend must be **Static Site**, not Docker. If you created frontend as Docker, delete and recreate as Static with Root Dir `frontend`, Build `npm install && npm run build`, Publish `dist`, rewrite `/* → /index.html`.

**Expected successful logs after fix:**
```
#1 [internal] load build definition from Dockerfile
#1 transferring dockerfile: 457B done
...
#5 [2/4] COPY backend/requirements.txt ./requirements.txt
#6 [3/4] RUN pip install ...
#7 DONE
==> Build successful
==> Starting service with 'uvicorn app.main:app --host 0.0.0.0 --port $PORT'
INFO: Application startup complete.
```

Backend health check `GET /health` should return 200.
