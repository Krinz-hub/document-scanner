# Architectural Decisions & Limitations

## Why no LLM?
Document extraction, OCR, validation and image analysis are specialized tasks. An LLM adds latency and uncertainty without replacing those components.

## Why no blockchain?
The MVP does not require decentralized consensus. Authenticity depends on authoritative document/registry systems and physical/visual evidence, not a blockchain ledger.

## Why no microservices initially?
The system has modular boundaries but does not need distributed deployment complexity during the prototype stage. A modular monolith is easier to test and operate.

## Why rules instead of an ML risk model?
Rules are inspectable and auditable. A learned risk model would require representative labeled data, calibration, threshold selection and ongoing validation.

## Why evidence instead of a single score?
A score without reasons cannot tell an officer what needs checking and makes debugging difficult.

## Tampering limitation
Tampering detection is inherently difficult. Performance depends heavily on document types, capture conditions, genuine/forged training data and reference material.

## Stamp limitation
Stamp authenticity should not be claimed without an appropriate reference set or authoritative verification.

## Face limitation
Face similarity can produce false matches and false non-matches. Thresholds must be evaluated on representative validation data.

## External verification limitation
No external status should be claimed when the authoritative source is unavailable.

## Data limitation
Identity documents contain sensitive personal information. Retention, access and processing must follow the applicable legal and organizational requirements.
