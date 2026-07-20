#!/bin/bash
set -euo pipefail

PGDATA="${PGDATA:-/var/lib/postgresql/data}"

if [ -z "$(ls -A "$PGDATA" 2>/dev/null)" ]; then
  echo "[entrypoint] Initializing PostgreSQL data directory..."
  gosu postgres initdb -D "$PGDATA" --auth=trust --username=postgres >/dev/null

  gosu postgres pg_ctl -D "$PGDATA" \
    -o "-c listen_addresses=127.0.0.1 -c unix_socket_directories=/var/run/postgresql" \
    -w start

  gosu postgres psql -v ON_ERROR_STOP=1 --username=postgres <<-EOSQL
    CREATE USER "${POSTGRES_USER}" WITH SUPERUSER PASSWORD '${POSTGRES_PASSWORD}';
    CREATE DATABASE "${POSTGRES_DB}" OWNER "${POSTGRES_USER}";
EOSQL

  gosu postgres pg_ctl -D "$PGDATA" -m fast -w stop
  echo "[entrypoint] PostgreSQL data directory ready."
fi

exec supervisord -c /etc/supervisor/conf.d/app.conf
