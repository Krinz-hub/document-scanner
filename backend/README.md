# Border Screening Platform — Backend

Modular monolith backend providing the document screening orchestrator, deterministic rule engine, and computer vision perception pipelines (OCR, MRZ parser, image tampering heuristics, and facial comparison).

## Architecture Boundaries
- **Runtime:** Python 3.11+
- **Framework:** FastAPI / Pydantic v2 / SQLAlchemy 2.0
- **Database:** PostgreSQL
- **Key Modules:**
  - `orchestrator`: Lifecycle coordinator and decision-support evidence builder.
  - `quality`: Document resolution, blur, and glare assessment.
  - `ocr`: Text bounding-box and field extraction (OpenCV + PaddleOCR).
  - `mrz`: ICAO 9303 MRZ parsing and checksum verification.
  - `rules`: Deterministic validation engine (dates, document numbers, cross-checks).
  - `tampering`: Multi-modal visual anomaly evidence collection.
  - `face`: Document portrait vs. live traveler face comparison.
  - `external`: Registry adapter interface (Mock / Authorized).
