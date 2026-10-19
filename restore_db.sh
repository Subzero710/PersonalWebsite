#!/usr/bin/env bash
# Rebuild a disposable Django development database and import a PostgreSQL custom-format
# dump (possibly from an older Django schema). No handwritten Django migrations.
set -Eeuo pipefail

DUMP="${1:-./portfolio_prod.dump}"
if [[ ! -s "$DUMP" ]]; then
  echo "Dump introuvable ou vide : $DUMP" >&2
  exit 1
fi
if [[ ! -f ./docker-compose.yml || ! -f ./backend/core/migrations/0001_initial.py ]]; then
  echo "Lancer depuis la racine de PersonalWebsite, avec ses migrations versionnées." >&2
  exit 1
fi
if [[ ! -f .env ]] || ! grep -Eq '^DJANGO_ALLOWED_HOSTS=.*(localhost|127\.0\.0\.1)' .env; then
  echo "Protection : ce script destructif exige DJANGO_ALLOWED_HOSTS=localhost (ou 127.0.0.1) dans .env." >&2
  exit 1
fi

COMPOSE=(docker compose)
STAGING="portfolio_import_$$_$RANDOM"
created_stage=0
cleanup() {
  if (( created_stage )); then
    "${COMPOSE[@]}" exec -T db sh -c 'dropdb -U "$POSTGRES_USER" --if-exists --force "$1"' _ "$STAGING" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

echo '[1/6] Arrêt des services web locaux ; démarrage PostgreSQL.'
"${COMPOSE[@]}" stop web nginx >/dev/null
"${COMPOSE[@]}" up -d db

echo '[2/6] Vérification du dump et restauration isolée.'
"${COMPOSE[@]}" exec -T db pg_restore --list < "$DUMP" > /dev/null
"${COMPOSE[@]}" exec -T db sh -c 'createdb -U "$POSTGRES_USER" -O "$POSTGRES_USER" "$1"' _ "$STAGING"
created_stage=1
"${COMPOSE[@]}" exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d "$1" --no-owner --no-acl --exit-on-error' _ "$STAGING" < "$DUMP"
"${COMPOSE[@]}" exec -T db sh -c "psql -U \"\$POSTGRES_USER\" -d \"\$1\" -Atc \"SELECT to_regclass('public.core_siteconfig') IS NOT NULL\" | grep -qx t" _ "$STAGING"

echo '[3/6] Construction de l’image Django actuelle.'
"${COMPOSE[@]}" build web

echo '[4/6] Suppression de la base de DÉVELOPPEMENT et reconstruction par les migrations Django.'
"${COMPOSE[@]}" exec -T db sh -c '
  set -eu
  dropdb -U "$POSTGRES_USER" --if-exists --force "$POSTGRES_DB"
  createdb -U "$POSTGRES_USER" -O "$POSTGRES_USER" "$POSTGRES_DB"
'
"${COMPOSE[@]}" run --rm -T --no-deps --entrypoint python web manage.py migrate --noinput

echo '[5/6] Copie des données historiques vers le nouveau schéma Django.'
"${COMPOSE[@]}" run --rm -T --no-deps -e IMPORT_SOURCE_DB="$STAGING" --entrypoint python web - <<'PY'
import os
import django
import psycopg
from psycopg import sql
from psycopg.rows import dict_row

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Portfolio.settings')
django.setup()

from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import connection, transaction
from django.db.models import Max
from core.models import SiteConfig, Tag, Project, Highlight, KPI, Skill

src = psycopg.connect(
    dbname=os.environ['IMPORT_SOURCE_DB'],
    user=os.environ['POSTGRES_USER'],
    password=os.environ['POSTGRES_PASSWORD'],
    host=os.environ.get('POSTGRES_HOST', 'db'),
    port=os.environ.get('POSTGRES_PORT', '5432'),
    row_factory=dict_row,
)


def table_exists(table):
    return src.execute('SELECT to_regclass(%s) IS NOT NULL AS found', (f'public.{table}',)).fetchone()['found']


def source_rows(table):
    if not table_exists(table):
        return []
    return src.execute(sql.SQL('SELECT * FROM {}').format(sql.Identifier(table))).fetchall()


imported_models = []


def import_model(model, source_table=None, remap=None):
    table = source_table or model._meta.db_table
    rows = source_rows(table)
    fields = {f.attname for f in model._meta.concrete_fields}
    objects = []
    for row in rows:
        vals = {k: v for k, v in row.items() if k in fields}
        if remap:
            vals = remap(vals)
            if vals is None:
                continue
        objects.append(model(**vals))
    for i in range(0, len(objects), 250):
        model.objects.bulk_create(objects[i:i + 250], batch_size=250)
    imported_models.append(model)
    print(f'  {table}: {len(objects)} lignes', flush=True)
    return len(objects)


with transaction.atomic():
    # Data sources may predate hero_title/intro/bio/icon_key/Skill; model defaults
    # populate those new optional columns, rather than patching database schema.
    import_model(SiteConfig)
    import_model(Tag)
    import_model(Project)
    import_model(Project.tags.through)
    import_model(Highlight)
    import_model(KPI)
    import_model(Skill)

    # Preserve production logins/password hashes and group memberships.
    import_model(Group)
    User = get_user_model()
    import_model(User)
    import_model(User.groups.through)

    # Django created its own content types and permissions for the NEW schema.
    # Never overwrite them with old IDs; map permissions by natural key.
    dest_perms = {
        (p.content_type.app_label, p.content_type.model, p.codename): p.pk
        for p in Permission.objects.select_related('content_type')
    }
    old_permission_rows = (
        src.execute('''
            SELECT p.id, ct.app_label, ct.model, p.codename
            FROM auth_permission p
            JOIN django_content_type ct ON ct.id = p.content_type_id
        ''').fetchall()
        if table_exists('auth_permission') and table_exists('django_content_type') else []
    )
    perm_ids = {
        p['id']: dest_perms.get((p['app_label'], p['model'], p['codename']))
        for p in old_permission_rows
    }

    def map_permission(vals):
        target_id = perm_ids.get(vals['permission_id'])
        if target_id is None:
            return None
        vals['permission_id'] = target_id
        return vals

    import_model(Group.permissions.through, remap=map_permission)
    import_model(User.user_permissions.through, remap=map_permission)

    new_contenttypes = {
        (ct.app_label, ct.model): ct.pk for ct in ContentType.objects.all()
    }
    legacy_contenttypes = {}
    for row in source_rows('django_content_type'):
        legacy_contenttypes[row['id']] = new_contenttypes.get((row['app_label'], row['model']))

    def map_log_entry(vals):
        old_content_type = vals.get('content_type_id')
        if old_content_type is not None:
            vals['content_type_id'] = legacy_contenttypes.get(old_content_type)
        return vals

    import_model(LogEntry, remap=map_log_entry)

    # Explicit primary keys were imported. Align generated PK sequences to avoid
    # collisions on subsequent writes in Django Admin.
    for model in imported_models:
        pk_value = model.objects.aggregate(max_id=Max('pk'))['max_id']
        if pk_value is None:
            continue
        with connection.cursor() as c:
            c.execute('SELECT pg_get_serial_sequence(%s, %s)', [model._meta.db_table, model._meta.pk.column])
            sequence = c.fetchone()[0]
            if sequence:
                c.execute('SELECT setval(%s::regclass, %s, true)', [sequence, pk_value])

src.close()
print('Import terminé : schéma actuel conservé, contenus importés, historique Django propre.')
PY

echo '[6/6] Redémarrage et vérifications.'
"${COMPOSE[@]}" up -d --force-recreate web nginx
"${COMPOSE[@]}" exec -T web python manage.py check
"${COMPOSE[@]}" exec -T web python manage.py makemigrations core --check --dry-run
"${COMPOSE[@]}" exec -T web python manage.py showmigrations core
echo 'Terminé. Important : le dump PostgreSQL ne contient pas les fichiers du volume media.'
