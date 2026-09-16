# API Specification

## Screening
`POST /api/v1/screenings`

Create a screening session.

`GET /api/v1/screenings/{id}`

Return current screening state.

## Document
`POST /api/v1/screenings/{id}/document`

Upload/capture document.

## Face
`POST /api/v1/screenings/{id}/face`

Submit live face capture.

## Evidence
`GET /api/v1/screenings/{id}/evidence`

Return normalized evidence.

## Health
`GET /api/v1/health`

Return service health.

## Example response

```json
{
  "screening_id": "SCR-001",
  "status": "REVIEW_REQUIRED",
  "verification": {
    "mrz": "PASS",
    "external": "VALID",
    "face": "MATCH"
  },
  "analysis": {
    "photo": "FLAG",
    "text": "PASS",
    "stamp": "INSUFFICIENT_EVIDENCE"
  },
  "reasons": [
    "DOB inconsistency",
    "Possible photo-region manipulation"
  ]
}
```
