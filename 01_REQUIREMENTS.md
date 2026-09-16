# Requirements

## Functional
1. Create screening session.
2. Capture/upload document.
3. Assess image quality.
4. Classify document type.
5. Extract text and fields.
6. Parse and validate MRZ where applicable.
7. Validate document rules.
8. Analyze possible tampering.
9. Capture/receive live face image.
10. Compare document portrait with live face.
11. Query an authorized registry through an adapter.
12. Aggregate evidence.
13. Generate explainable review priority.
14. Display results to officer.
15. Record audit events.

## Non-functional
- Secure transport and storage.
- Role-based access.
- Deterministic, reproducible results.
- Versioned models and rules.
- Graceful failure.
- Responsive UI.
- Accessible interface.
- Test coverage for critical validation logic.
- Measured model performance.

## Explicit non-requirements
- Automatic border admission/refusal.
- Universal forgery detection.
- Metadata-based forgery proof.
- LLM-based document verification.
- Blockchain.
- Kubernetes for the MVP.
