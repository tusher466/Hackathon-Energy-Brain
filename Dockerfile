# Stage 1: Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --only=production=false || npm install
COPY frontend/ ./
# Build with empty VITE_API_URL so it uses same-origin /api
ENV VITE_API_URL=""
ENV NODE_ENV=production
RUN npm run build

# Stage 2: Backend with frontend bundled - production ready, 502 fix for Render free tier
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV PYTHONDONTWRITEBYTECODE=1

# System deps for opencv + curl for healthcheck, no useradd to avoid permission issues on Render
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 curl && \
    rm -rf /var/lib/apt/lists/*

# Install python deps first for cache
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Copy frontend dist from stage 1 into locations backend expects (for single URL full-stack)
COPY --from=frontend-build /app/frontend/dist ./frontend/dist
COPY --from=frontend-build /app/frontend/dist ./static
# Copy landing page
COPY landing ./landing

# Ensure writable for SQLite (Render ephemeral, no volume needed but need write perms)
RUN chmod -R 775 /app && \
    touch /app/energy_brain.db || true && \
    chmod 664 /app/energy_brain.db || true

EXPOSE 8000

# Market-ready healthcheck - lenient for cold start free tier (60s start, curl fallback to wget)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/health || curl -f http://localhost:${PORT}/health || wget -qO- http://localhost:8000/health || exit 1

# Production run - SINGLE worker to avoid OOM on free tier 512MB (2 workers caused 502)
# Use sh -c to ensure $PORT expansion works on Render
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --log-level info"]
