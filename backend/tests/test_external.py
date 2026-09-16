"""Tests for Module 7: External Registry Provider Adapters."""

from backend.app.modules.external import MockRegistryProvider, AuthorizedGovernmentProvider


def test_mock_registry_valid_document():
    provider = MockRegistryProvider()
    res = provider.verify_document("P12345678", "USA")

    assert res["status"] == "VALID"
    assert res["is_mock"] is True
    assert "active" in res["reason"].lower()


def test_mock_registry_revoked_document():
    provider = MockRegistryProvider()
    res = provider.verify_document("STOLEN-999", "CAN")

    assert res["status"] == "REVOKED"
    assert res["is_mock"] is True
    assert "stolen" in res["reason"].lower()


def test_mock_registry_timeout_status_rule():
    provider = MockRegistryProvider()
    res = provider.verify_document("TIMEOUT-001", "GBR")

    # Critical rule: Unavailable must NEVER become Valid or Invalid
    assert res["status"] == "UNAVAILABLE"
    assert res["is_mock"] is True


def test_authorized_provider_unconfigured_defaults_to_unavailable():
    # If unconfigured endpoint is used, must return UNAVAILABLE rather than crashing
    provider = AuthorizedGovernmentProvider(endpoint="")
    res = provider.verify_document("A12345678", "FRA")

    assert res["status"] == "UNAVAILABLE"
    assert res["is_mock"] is False
