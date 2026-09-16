# Implementation Steps — One by One

Do not jump ahead. Complete and test each step before starting the next.

## Phase 0 — Repository
1. Create repository.
2. Create `frontend/` and `backend/`.
3. Add `.env.example`.
4. Add README.
5. Add Git ignore.
6. Add Docker baseline.
7. Define branch/commit convention.

**Done when:** project starts locally from a clean clone.

---

## Phase 1 — Backend Foundation
8. Create FastAPI app.
9. Add `/api/v1/health`.
10. Add configuration management.
11. Add structured logging.
12. Add PostgreSQL connection.
13. Add SQLAlchemy models.
14. Add migrations.
15. Add pytest setup.

**Done when:** API, database and tests run locally.

---

## Phase 2 — Frontend Foundation
16. Create Next.js app.
17. Add TypeScript strict mode.
18. Add Tailwind.
19. Create global CSS/tokens.
20. Create AppShell.
21. Create typography and spacing system.
22. Create status component.
23. Create data-row component.

**Done when:** UI has stable styling and no page-specific CSS hacks.

---

## Phase 3 — Screening Lifecycle
24. Create screening API.
25. Create screening database record.
26. Create screening page.
27. Connect frontend to backend.
28. Add loading/error/empty states.

**Done when:** user can create and view a screening.

---

## Phase 4 — Document Input
29. Add document upload.
30. Validate file type and size.
31. Store permitted image securely.
32. Generate object reference.
33. Display document preview.
34. Add image-quality endpoint.

**Done when:** a test document can be uploaded and rejected/accepted based on quality.

---

## Phase 5 — OCR
35. Integrate OpenCV preprocessing.
36. Integrate PaddleOCR.
37. Extract text.
38. Store bounding boxes/confidence.
39. Build field extraction.
40. Display extracted fields.
41. Add OCR tests.

**Done when:** test documents produce structured fields with confidence.

---

## Phase 6 — MRZ
42. Detect/read MRZ.
43. Parse MRZ fields.
44. Implement checksum validation.
45. Compare MRZ and visual fields.
46. Display inconsistencies.

**Done when:** deliberately altered test data produces the expected inconsistency.

---

## Phase 7 — Rules Engine
47. Create versioned ruleset structure.
48. Implement required-field checks.
49. Implement date checks.
50. Implement expiry.
51. Implement document-number checks.
52. Implement cross-field checks.
53. Store rule evidence.
54. Add unit tests for every rule.

**Done when:** rules are deterministic and fully tested.

---

## Phase 8 — Tampering MVP
55. Define the exact tampering dataset.
56. Build photo-region extraction.
57. Implement baseline OpenCV analysis.
58. Create tampering model only if baseline evidence is insufficient.
59. Evaluate on held-out data.
60. Store confidence and model version.
61. Display evidence regions.

**Done when:** the system reports measured performance and known limitations.

---

## Phase 9 — Face Verification
62. Extract document portrait.
63. Capture live face.
64. Add face quality checks.
65. Add face detection.
66. Add face embedding/comparison.
67. Choose threshold using validation data.
68. Test false matches/non-matches.
69. Display result and quality.

**Done when:** performance is measured rather than assumed.

---

## Phase 10 — External Verification
70. Define provider adapter interface.
71. Implement mock registry for development.
72. Mark mock responses clearly.
73. Add timeout/error handling.
74. Add real authorized API only when access is legitimately available.
75. Never treat unavailable as valid.

**Done when:** valid, revoked, not-found and unavailable states are distinguishable.

---

## Phase 11 — Evidence + Review
76. Normalize all module outputs.
77. Create evidence schema.
78. Implement review-priority rules.
79. Generate human-readable reasons.
80. Add evidence drawer.
81. Add manual-review action.

**Done when:** every review flag can be traced to evidence.

---

## Phase 12 — Audit + Security
82. Add authentication.
83. Add role checks.
84. Add audit events.
85. Add encryption configuration.
86. Add retention/deletion policy hooks.
87. Remove sensitive data from normal logs.
88. Add security tests.

**Done when:** access and audit behavior can be demonstrated.

---

## Phase 13 — End-to-End Testing
89. Build clean-document test set.
90. Build altered-document test set.
91. Build low-quality test set.
92. Build face-match/non-match test set.
93. Test external API failures.
94. Test module failures.
95. Measure end-to-end latency.
96. Record false-positive/false-negative behavior.

**Done when:** the system fails safely and results are measurable.

---

## Phase 14 — Deployment
97. Create production Dockerfiles.
98. Add Nginx/HTTPS configuration.
99. Configure PostgreSQL.
100. Configure object storage.
101. Add monitoring.
102. Add backup strategy.
103. Run clean-environment deployment.

**Done when:** another machine can deploy the documented system.

---

# Golden Rule

Never implement step N+1 because it “looks cool” if step N is not tested.

The correct order is:

`Build → Test → Measure → Document → Continue`
