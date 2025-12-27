# ---- Stage UI (TS -> main.js) ----
FROM node:22-alpine AS ui
WORKDIR /app/ui

COPY ui/package.json ui/package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

COPY ui/ .
# ton build écrit dans ../core/static/... => il faut que le dossier existe
RUN mkdir -p /app/core/static/core/dist
RUN npm run build


# ---- Stage App (Django) ----
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy generated bundle by esbuild
COPY --from=ui /app/core/static/core/dist/main.js /app/core/static/core/dist/main.js
COPY --from=ui /app/core/static/core/dist/main.js.map /app/core/static/core/dist/main.js.map

# Entrypoint + user
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh
RUN useradd -m appuser && chown -R appuser:appuser /app

ENTRYPOINT ["/app/entrypoint.sh"]
