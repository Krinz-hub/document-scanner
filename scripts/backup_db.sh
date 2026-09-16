#!/usr/bin/env bash
# ==============================================================================
# Border Screening Platform - Automated Database Backup Script
# Step 102: Backup Strategy
# ==============================================================================
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-border_screening_postgres}"
POSTGRES_USER="${POSTGRES_USER:-screening_admin}"
POSTGRES_DB="${POSTGRES_DB:-border_screening}"

mkdir -p "${BACKUP_DIR}"

BACKUP_FILE="${BACKUP_DIR}/border_screening_${POSTGRES_DB}_${TIMESTAMP}.sql.gz"

echo "========================================================"
echo " Starting Database Backup: ${POSTGRES_DB}"
echo " Timestamp: ${TIMESTAMP}"
echo " Target:    ${BACKUP_FILE}"
echo "========================================================"

# Detect whether running inside docker compose or directly
if docker ps --format '{{.Names}}' | grep -q "${POSTGRES_CONTAINER}"; then
    echo "[*] Dumping from running container: ${POSTGRES_CONTAINER}..."
    docker exec -e PGPASSWORD="${POSTGRES_PASSWORD:-screening_dev_password}" "${POSTGRES_CONTAINER}" \
        pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" --no-owner --no-acl | gzip -9 > "${BACKUP_FILE}"
else
    echo "[*] Dumping from local postgres host..."
    PGPASSWORD="${POSTGRES_PASSWORD:-screening_dev_password}" pg_dump \
        -h "${POSTGRES_HOST:-localhost}" \
        -p "${POSTGRES_PORT:-5432}" \
        -U "${POSTGRES_USER}" \
        -d "${POSTGRES_DB}" \
        --no-owner --no-acl | gzip -9 > "${BACKUP_FILE}"
fi

# Verify backup existence and non-zero size
if [ -s "${BACKUP_FILE}" ]; then
    FILESIZE=$(ls -lh "${BACKUP_FILE}" | awk '{print $5}')
    echo "[+] SUCCESS: Backup completed successfully. File size: ${FILESIZE}"
else
    echo "[-] ERROR: Backup file is missing or empty!" >&2
    exit 1
fi

# Apply retention policy: delete backups older than RETENTION_DAYS
echo "[*] Purging backups older than ${RETENTION_DAYS} days in ${BACKUP_DIR}..."
find "${BACKUP_DIR}" -type f -name "border_screening_*.sql.gz" -mtime +"${RETENTION_DAYS}" -exec rm -f {} \;

echo "[+] Retention check complete."
echo "========================================================"
