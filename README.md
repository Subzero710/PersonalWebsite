# PersonalWebsite (Django Portfolio)

This is an Admin-first portfolio website built with Django + PostgreSQL + Nginx + Gunicorn.

## Run (Docker)

Create `.env` at repo root:

```env
DJANGO_SECRET_KEY=xxxx
DJANGO_ALLOWED_HOSTS=localhost
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost

POSTGRES_DB=xxxx
POSTGRES_USER=xxxx
POSTGRES_PASSWORD=xxxx
POSTGRES_HOST=xxxx
POSTGRES_PORT=xxxx
```

Start:

```bash
docker compose up --build
```

Open:
- http://localhost/
- http://localhost/admin/

Create admin user:

```bash
docker compose exec web python manage.py createsuperuser
```

## Content management

All content is managed in Django Admin:
- Site config (name, links, resume/CV, avatar)
- Projects + tags
- Highlights + KPIs (home page)

## UI build

The UI is bundled with esbuild from `backend/ui` into:
- `backend/core/static/core/dist/main.js`

## Deployment

The public entry point is `nginx`

```bash
docker compose up --build -d
```

## HTTPS

Enable HTTPS using Let’s Encrypt (recommended: `certbot --webroot`). Add a deploy hook to reload nginx after renewals.
