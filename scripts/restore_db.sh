#!/usr/bin/env bash
# ==============================================================================
# Border Screening Platform - Database Restore Script
# Step 102: Backup & Recovery Strategy
# ==============================================================================
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <path-to-backup.sql.gz>" >&2
    exit 1
fi

BACKUP_FILE="$1"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-border_screening_postgres}"
POSTGRES_USER="${POSTGRES_USER:-screening_admin}"
POSTGRES_DB="${POSTGRES_DB:-border_screening}"

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "[-] ERROR: Backup file not found: ${BACKUP_FILE}" >&2
    exit 1
fi

echo "========================================================"
echo " Restoring Database: ${POSTGRES_DB}"
echo " Source File:        ${BACKUP_FILE}"
echo " Container:          ${POSTGRES_CONTAINER}"
echo "========================================================"

if docker ps --format '{{.Names}}' | grep -q "${POSTGRES_CONTAINER}"; then
    echo "[*] Restoring into running container: ${POSTGRES_CONTAINER}..."
    gunzip -c "${BACKUP_FILE}" | docker exec -i -e PGPASSWORD="${POSTGRES_PASSWORD:-screening_dev_password}" \
        "${POSTGRES_CONTAINER}" psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"
else
    echo "[*] Restoring into local postgres host..."
    gunzip -c "${BACKUP_FILE}" | PGPASSWORD="${POSTGRES_PASSWORD:-screening_dev_password}" \
        psql -h "${POSTGRES_HOST:-localhost}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"
fi

echo "[+] SUCCESS: Database restoration completed."
echo "========================================================"
