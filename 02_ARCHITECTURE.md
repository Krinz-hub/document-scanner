# System Architecture

```text
Officer UI
   ↓
API / Authentication
   ↓
Screening Orchestrator
   ↓
Image Quality
   ↓
Document Classification
   ↓
OCR + MRZ
   ↓
Canonical Document Data
   ├── Rule Validation
   ├── Tampering Analysis
   ├── Face Verification
   └── External Verification
              ↓
       Evidence Aggregator
              ↓
       Review Priority
              ↓
        Officer Dashboard
              ↓
        Human Action
              ↓
          Audit Trail
```

## Backend boundaries

### API layer
Authentication, request validation and routing.

### Orchestrator
Controls workflow and module execution.

### AI/CV services
OCR, classification, tampering and face processing.

### Rules engine
Expiry, format, checksum and consistency checks.

### Verification adapter
Abstracts external authorized registries.

### Evidence layer
Normalizes outputs from every module.

### Persistence
PostgreSQL for structured records; S3-compatible object storage for permitted images.

## Do not over-engineer
Start as a modular monolith. Split into services only when scale, isolation, deployment or hardware requirements justify it.
