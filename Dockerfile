FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

ENV PORT=8000
ENV WORKERS=4
ENV DATABASE_PATH=/app/data/traffic.db
ENV SNAPSHOTS_DB_PATH=/app/data/snapshots.db
ENV WEBHOOKS_DB_PATH=/app/data/webhooks.db

EXPOSE ${PORT}

CMD gunicorn api.main:app \
    -w ${WORKERS} \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT} \
    --graceful-timeout 30 \
    --timeout 120
