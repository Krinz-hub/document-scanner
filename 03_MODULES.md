# Module Specifications

## Module 1 — Image Quality
### Input
Document image.

### Checks
Blur, resolution, glare, orientation, crop and document visibility.

### Output
Quality status, score, issues.

### Failure
Request recapture.

---

## Module 2 — Document Classification
### Input
Document image.

### Output
Passport, visa, ID, permit, licence or unknown + confidence.

### Failure
Unknown/low-confidence classification.

---

## Module 3 — OCR + MRZ
### Stack
OpenCV + PaddleOCR + Python MRZ validation.

### Output
Fields, bounding boxes, OCR confidence and raw/parsed MRZ.

### Important
Visible fields and MRZ should be cross-validated.

---

## Module 4 — Rule Validation
### Stack
Python rules engine.

### Checks
Required fields, formats, expiry, check digits, cross-field consistency and document-specific rules.

### Principle
Do not use ML for deterministic rules.

---

## Module 5 — Tampering Analysis
### Stack
OpenCV + PyTorch.

### Regions
Photo, text, stamps, background/security features.

### Output
Observed anomaly, region, confidence and evidence.

### Limitation
A visual anomaly is not automatically proof of forgery.

---

## Module 6 — Face Verification
### Stack
InsightFace/OpenCV.

### Flow
Document portrait → face detection → quality → embedding
and
Live face → detection → quality → embedding
→ similarity.

### Output
Match/review/low similarity + quality and threshold metadata.

---

## Module 7 — External Verification
### Input
Normalized document identifiers.

### Output
Valid, expired, revoked, not found, inconsistent or unavailable.

### Prototype
Use a clearly labeled simulated registry if an authorized real API is unavailable.

---

## Module 8 — Evidence Aggregator
Collects module results without inventing evidence.

---

## Module 9 — Review Priority
Initially use explainable rules. Do not start with an unexplained 0–100 score.

---

## Module 10 — Audit
Record screening ID, timestamp, checks, results, model versions, ruleset versions and officer actions.
