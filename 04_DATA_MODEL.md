# Data Model

## screening
- id
- created_at
- checkpoint_id
- status
- review_priority

## document
- screening_id
- type
- document_number_hash
- issue_date
- expiry_date
- object_reference

## extracted_fields
- screening_id
- field_name
- value/reference
- confidence
- source

## validation_result
- screening_id
- check_name
- status
- evidence
- ruleset_version

## tampering_result
- screening_id
- region
- detector
- status
- confidence
- evidence
- model_version

## face_result
- screening_id
- similarity
- quality
- status
- model_version

## external_check
- screening_id
- provider
- status
- response_reference
- checked_at

## evidence
- screening_id
- category
- severity
- explanation
- source_module

## audit_event
- screening_id
- event_type
- timestamp
- actor
- metadata

## model_version
- model_name
- version
- dataset_version
- evaluation_reference
- limitations

## ruleset_version
- ruleset_name
- version
- effective_from
- documentation_reference
