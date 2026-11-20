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

# Stage 2: Backend with frontend bundled - production ready
FROM python:3.11-slim
WORKDIR /app

# System deps for opencv + security updates, create non-root user
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 curl && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -m -u 1001 appuser

# Install python deps
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./
# Fix permissions
RUN chown -R appuser:appuser /app

# Copy frontend dist from stage 1 into locations backend expects
COPY --from=frontend-build /app/frontend/dist ./frontend/dist
COPY --from=frontend-build /app/frontend/dist ./static
# Copy landing page (HTML+CSS only) for /landing route
COPY landing ./landing

# Make sure static files owned by appuser
RUN chown -R appuser:appuser /app/frontend /app/static /app/landing || true

EXPOSE 8000

# Healthcheck for market deployment
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

USER appuser

# Production run - workers 2, log level info
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2 --log-level info
