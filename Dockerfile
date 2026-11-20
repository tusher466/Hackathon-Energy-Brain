FROM python:3.11-slim

WORKDIR /app

# System deps for opencv
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# Install python deps from backend
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend app
COPY backend/ ./

EXPOSE 8000

# Render sets $PORT, fallback to 8000 for local docker
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
