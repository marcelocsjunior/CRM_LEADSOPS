#!/usr/bin/env bash
set -euo pipefail

DB_PATH="${LEADOPS_DB:-/opt/leadops/data/leadops.db}"
BACKUP_DIR="${LEADOPS_BACKUP_DIR:-/opt/leadops/data/backups}"
RETENTION_DAYS="${LEADOPS_BACKUP_RETENTION_DAYS:-7}"

if [[ ! -f "$DB_PATH" ]]; then
  echo "Banco não encontrado: $DB_PATH" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"
chmod 750 "$BACKUP_DIR"

STAMP="$(date +%Y%m%d_%H%M%S)"
TARGET="$BACKUP_DIR/leadops_${STAMP}.db"

sqlite3 "$DB_PATH" ".backup '$TARGET'"
chmod 640 "$TARGET"

find "$BACKUP_DIR" -type f -name 'leadops_*.db' -mtime +"$RETENTION_DAYS" -delete

echo "Backup criado: $TARGET"
