# Border Document Screening Platform

An AI-assisted border document screening platform for passports, visas, national IDs, permits, and other identity/travel documents.

> **Operational Principle:** This system provides **decision support for trained officers**, not an automated verdict engine. It never outputs unexplained assertions (e.g. "FAKE" or a raw "94% risk score"). Instead, it aggregates structured, explainable evidence across deterministic validation rules, perceptual computer vision checks, and registry queries to present human-actionable review priorities.

---

## System Architecture

```text
Document + Live Person
        │
        ▼
Image Quality Check (DPI, Blur, Glare)
        │
        ▼
Document Type Classification
        │
        ▼
OCR + MRZ Extraction
        │
        ▼
Canonical Document Data
        │
        ├────────────────────────┐
        │                        │
        ▼                        ▼
Rule Validation           Tampering Analysis
(Dates, Expiry, Checksums)(Boundaries, Noise, Splicing)
        │                        │
        └───────────┬────────────┘
                    │
                    ▼
           Face Verification
        (Passport vs Live Person)
                    │
                    ▼
          External Verification
        (Registry Adapter: Mock/Auth)
                    │
                    ▼
          Evidence Aggregator
                    │
                    ▼
     Explainable Review Priority (LOW / MEDIUM / HIGH)
                    │
                    ▼
      Officer Dashboard (Next.js)
                    │
                    ▼
         Human Review / Action
                    │
                    ▼
        Immutable Audit Trail
```

---

## Core Philosophy & Design Rules

1. **Deterministic Logic First:** Fields, date validity, document expiration, check digits, and cross-field consistency use deterministic software algorithms — never generative models or non-deterministic heuristics.
2. **Perception Where Required:** Machine learning and computer vision (OpenCV, PaddleOCR, PyTorch, InsightFace) are used strictly where sensory perception is necessary.
3. **Structured Evidence over Black-Box Scores:** Every module emits structured evidence with status (`VALID`, `INVALID`, `REVIEW`, `UNAVAILABLE`, `INSUFFICIENT_EVIDENCE`, `LOW_IMAGE_QUALITY`), confidence, affected field/bounding box, and module version.
4. **Calibrated Operational UI:** High-density, professional interface adhering to operational tokens (`--bg`, `--surface`, `--line`, `--text`). Zero decorative AI clutter, glassmorphism, or fake animations.
5. **Simplicity over Premature Distribution (Ponytail Principle):** Built as a **modular monolith**. Excludes Kubernetes, Kafka, Redis, GraphQL, and microservices until measurable performance demands them.

---

## Technology Stack

- **Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, PostgreSQL, Alembic
- **Computer Vision & ML:** OpenCV (`opencv-python-headless`), PaddleOCR, PyTorch, InsightFace
- **Frontend:** Next.js, TypeScript (Strict Mode), Tailwind CSS, Playwright
- **Storage:** MinIO (Local development) / S3-compatible object storage
- **Infrastructure:** Docker, Docker Compose, Nginx

---

## Repository Structure

```text
border_screening_architecture_docs/
├── backend/               # FastAPI modular monolith & CV pipeline
├── frontend/              # Next.js officer operational dashboard
├── .env.example           # Centralized configuration blueprint
├── docker-compose.yml     # Local services (PostgreSQL, MinIO, Backend, Frontend)
├── 00_MASTER_PLAN.md      # Core platform strategy and non-goals
├── 01_REQUIREMENTS.md     # Functional & security requirements
├── 02_ARCHITECTURE.md     # Component topology & orchestrator workflow
├── 03_MODULES.md          # Detailed module interfaces
├── 04_DATA_MODEL.md       # Canonical data schemas & evidence structures
├── 05_API.md              # REST API endpoint specifications
├── 06_UI_DESIGN.md        # Officer design system & interaction tokens
├── 07_TECH_STACK.md       # Tech constraints & excluded libraries
├── 08_IMPLEMENTATION_STEPS.md # 103-step sequential roadmap
└── 09_DECISIONS_AND_LIMITATIONS.md # Known trade-offs & limitations
```

---

## Quick Start (Local Development)

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 20+

### 2. Configure Environment
```bash
cp .env.example .env
```

### 3. Start Supporting Infrastructure (Step 6+)
```bash
docker compose up -d postgres minio
```

---

## Implementation Roadmap

The platform is constructed strictly **one verified step at a time** across 15 phases:
- **Phase 0:** Repository Foundation (Steps 1–7)
- **Phase 1:** Backend Foundation (Steps 8–15)
- **Phase 2:** Frontend Foundation (Steps 16–23)
- **Phase 3:** Screening Lifecycle (Steps 24–28)
- **Phase 4:** Document Input & Quality (Steps 29–34)
- **Phase 5:** OCR & Field Extraction (Steps 35–41)
- **Phase 6:** MRZ Parsing & Validation (Steps 42–46)
- **Phase 7:** Rules Engine (Steps 47–54)
- **Phase 8:** Tampering Heuristics (Steps 55–61)
- **Phase 9:** Face Comparison (Steps 62–69)
- **Phase 10:** External Registry Adapters (Steps 70–75)
- **Phase 11:** Evidence Aggregator & Review (Steps 76–81)
- **Phase 12:** Audit Trail & Security (Steps 82–88)
- **Phase 13:** End-to-End Evaluation (Steps 89–96)
- **Phase 14:** Production Hardening & Deployment (Steps 97–103)
