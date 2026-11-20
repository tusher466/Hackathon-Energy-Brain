# Deploy Energy Brain to Render – Step by Step

Repo already pushed to https://github.com/tusher466/Hackathon-Energy-Brain with `render.yaml` blueprint.

## Option A – Blueprint (Recommended, 2 services auto)

1. Go to https://dashboard.render.com/ → **New +** → **Blueprint**
2. Connect GitHub account and select repo `tusher466/Hackathon-Energy-Brain`
3. Render detects `render.yaml` with 2 services:
   - `energy-brain-backend` (Python)
   - `energy-brain-frontend` (Static)
4. Click **Apply**. Render will:
   - Build backend: `pip install -r requirements.txt`
   - Start backend: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Health check `/health`
   - Build frontend: `npm install && npm run build`
   - Publish `frontend/dist` with SPA rewrite `/* → /index.html`
5. After first deploy, backend URL will be `https://energy-brain-backend.onrender.com`
   - If frontend built before backend URL known, set env var `VITE_API_URL` in frontend service to backend URL and **Manual Deploy → Clear build cache & Deploy**
6. Set CORS in backend: In Render dashboard → backend service → Environment → add `CORS_ORIGINS` = `https://energy-brain-frontend.onrender.com,https://your-frontend-url.onrender.com`
7. Optional secrets: add `NREL_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` in backend env (sync: false). App works without them – synthetic fallback.

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
