# Border Document Screening Platform — Production Deployment Guide

This document defines the production hardening, container orchestration, monitoring, backup, and clean-environment deployment procedures for the **Border Document Screening Platform** (Phases 0–14).

---

## 1. System Architecture & Topology

The production platform is deployed as an auditable, high-throughput **modular monolith** fronted by an Nginx reverse proxy with hardened security headers:

```text
                        Internet / Border Inspection LAN
                                      │
                                      ▼
                   ┌──────────────────────────────────────┐
                   │        Nginx Reverse Proxy           │
                   │   Port 80 (HTTP) / Port 443 (HTTPS)  │
                   │   - Security Headers (CSP, HSTS)     │
                   │   - Upload Limits (50MB Scan Max)    │
                   │   - Gzip Compression                 │
                   └──────────────────┬───────────────────┘
                                      │
                 ┌────────────────────┴────────────────────┐
                 │                                         │
                 ▼                                         ▼
   ┌───────────────────────────┐             ┌───────────────────────────┐
   │    Next.js Frontend       │             │      FastAPI Backend      │
   │  Standalone Node.js Server│             │   Uvicorn Production      │
   │  Port 3000 (Internal)     │             │   Port 8000 (Internal)    │
   │  Non-root: nextjs (1001)  │             │   Non-root: appuser(10001)│
   └───────────────────────────┘             └─────────────┬─────────────┘
                                                           │
                                ┌──────────────────────────┴───────────────┐
                                │                                          │
                                ▼                                          ▼
                 ┌─────────────────────────────┐            ┌─────────────────────────────┐
                 │    PostgreSQL 16 Engine     │            │    MinIO Object Storage     │
                 │   Port 5432 (Internal)      │            │   Port 9000 (Internal)      │
                 │   - Healthcheck: pg_isready │            │   - Healthcheck: mc ready   │
                 │   - Persistent Volume       │            │   - Auto-provisioned bucket │
                 └─────────────────────────────┘            └─────────────────────────────┘
```

---

## 2. Prerequisites & Requirements

- **Operating System:** Linux (Ubuntu 22.04 LTS+, Debian 12+, RHEL 9+) or macOS with Docker Desktop.
- **Container Engine:** Docker 24.0+ & Docker Compose v2.20+.
- **Resource Allocation:**
  - Minimum: 2 CPU cores, 4 GB RAM, 20 GB SSD storage.
  - Recommended (Operational Border Post): 4+ CPU cores, 8 GB RAM, 100 GB NVMe storage.

---

## 3. Clean-Environment Single-Command Launch (Step 103)

To launch the complete platform on a fresh host with zero pre-existing containers:

### 1. Clone & Configure
```bash
git clone <repository_url> border_screening_platform
cd border_screening_platform

# Copy and review production environment variables
cp .env.example .env.prod
```

### 2. Build & Launch Production Stack
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### 3. Verify Container Health
```bash
docker compose -f docker-compose.prod.yml ps
```
All containers (`postgres`, `minio`, `backend`, `frontend`, `nginx`) should report `healthy` or `running`.

---

## 4. Verification & Operational Probes

### Gateway Health Check
```bash
curl -i http://localhost/healthz
# Expected HTTP 200 OK -> "healthy"
```

### Backend Operational & Database Health
```bash
curl -i http://localhost/api/v1/health
# Expected HTTP 200 OK:
# {"status":"healthy","app":"Border Document Screening Engine","database":"connected","version":"1.0.0"}
```

### Prometheus Metrics Endpoint (Step 101)
```bash
curl -i http://localhost/metrics
# Expected Prometheus format telemetry:
# border_screenings_total 0
# border_screenings_status{status="REVIEW_REQUIRED"} 0
# border_documents_processed_total 0
# border_system_healthy 1
```

### Officer Dashboard UI
Open your browser at:
`http://localhost` (or the server's LAN IP address).

---

## 5. Automated Database Backup & Recovery (Step 102)

The system includes automated, non-disruptive database backup scripts with gzip compression and retention pruning.

### Executing a Backup
```bash
./scripts/backup_db.sh
```
- Output: `./backups/border_screening_border_screening_<TIMESTAMP>.sql.gz`
- Automatically prunes archives older than `RETENTION_DAYS` (default: 14 days).

### Scheduled Automated Backups (Cron)
Add the following line to the host's `crontab -e` to run daily backups at 02:00:
```cron
0 2 * * * cd /path/to/border_screening_architecture_docs && ./scripts/backup_db.sh >> /var/log/border_screening_backup.log 2>&1
```

### Restoring from Backup
```bash
./scripts/restore_db.sh ./backups/border_screening_border_screening_<TIMESTAMP>.sql.gz
```

---

## 6. Security Hardening Checklist

1. **Principle of Least Privilege:**
   - Backend runs as non-root `appuser` (UID 10001).
   - Frontend runs as non-root `nextjs` (UID 1001).
2. **Reverse Proxy Headers:**
   - Strict `Content-Security-Policy`, `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff`.
   - Client body size restricted to 50MB to prevent denial-of-service via oversized scan payloads.
3. **Sensitive Data Redaction:**
   - Document numbers and biometric vectors are never written in plain text to application logs.
   - PII identifiers are irreversibly hashed using SHA-256 (`hash_identifier`).
4. **Data Retention & Purge:**
   - Automated retention purge hook (`POST /api/v1/maintenance/retention/purge`) removes expired document scans in compliance with border data retention regulations.
5. **Role-Based Access Control (RBAC):**
   - Endpoints require authorized roles (`PRIMARY_OFFICER`, `SUPERVISOR`, `AUDITOR`) when `AUTH_REQUIRED=true`.

---

## 7. Zero-Downtime Migration & Updates

To update the platform with zero data loss:

```bash
# 1. Pull latest code
git pull origin main

# 2. Run database migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 3. Rebuild and restart services gracefully
docker compose -f docker-compose.prod.yml up -d --build --no-deps backend frontend

# 4. Verify end-to-end functionality
curl -f http://localhost/api/v1/health
```
