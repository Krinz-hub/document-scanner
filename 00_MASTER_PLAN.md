# Border Document Screening — Master Plan

## Goal
Build an explainable AI-assisted document screening platform for trained border officers.

## Core flow
Capture → Quality → Document Type → OCR/MRZ → Validation → Tampering Analysis → External Verification → Face Verification → Evidence → Review Priority → Officer Action → Audit

## Non-negotiable principles
- No black-box “fake/real” claim.
- No fake government/API claims.
- Deterministic checks use normal rules.
- AI is used only where visual/perceptual learning is useful.
- Every result has evidence, confidence, and model/ruleset version.
- Uncertainty is a valid output.
- Human officer remains responsible for the final action.
- Minimize retention of identity documents.
- Do not add infrastructure without a demonstrated need.

## Definition of done
A screening can be created, a test document can be processed end-to-end, each module returns structured evidence, the dashboard explains the result, failures are handled safely, and the complete event is auditable.
