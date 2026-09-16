"""Tests for Module 4: Deterministic Rules Engine."""

from backend.app.modules.rules import rules_engine


def test_rules_valid_document():
    valid_doc = {
        "name": "ANNA MARIA ERIKSSON",
        "document_number": "L898902C3",
        "nationality": "UTO",
        "date_of_birth": "1990-05-15",
        "expiry_date": "2030-10-20",
    }

    res = rules_engine.evaluate(valid_doc)
    assert res["overall_status"] == "PASS"
    assert len(res["evidence_items"]) == 0


def test_rules_expired_document_flagged():
    expired_doc = {
        "name": "JOHN DOE",
        "document_number": "A12345678",
        "nationality": "USA",
        "date_of_birth": "1980-01-01",
        "expiry_date": "2020-01-01",  # Expired
    }

    res = rules_engine.evaluate(expired_doc)
    assert res["overall_status"] == "FAIL"
    assert any("expired" in e["explanation"].lower() for e in res["evidence_items"])


def test_rules_future_dob_anomaly():
    future_dob_doc = {
        "name": "TIME TRAVELER",
        "document_number": "B98765432",
        "nationality": "CAN",
        "date_of_birth": "2045-06-01",  # Future date
        "expiry_date": "2050-01-01",
    }

    res = rules_engine.evaluate(future_dob_doc)
    assert res["overall_status"] == "FAIL"
    assert any("future" in e["explanation"].lower() for e in res["evidence_items"])


def test_rules_missing_required_fields():
    incomplete_doc = {
        "name": "INCOMPLETE PERSON",
        # missing document_number, nationality, etc.
    }

    res = rules_engine.evaluate(incomplete_doc)
    assert res["overall_status"] == "FAIL"
    assert any("missing" in e["explanation"].lower() for e in res["evidence_items"])
