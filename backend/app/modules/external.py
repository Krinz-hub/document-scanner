"""Module 7: External Verification Provider Adapter Architecture."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
from backend.app.config import get_settings

settings = get_settings()


class ExternalVerificationProvider(ABC):
    @abstractmethod
    def verify_document(
        self, document_number: str, nationality: str, document_type: str = "PASSPORT"
    ) -> Dict[str, Any]:
        """Query registry and return normalized status: VALID, EXPIRED, REVOKED, NOT_FOUND, UNAVAILABLE."""
        pass


class MockRegistryProvider(ExternalVerificationProvider):
    """Mock registry adapter for local development and integration testing."""

    PROVIDER_NAME = "MOCK_REGISTRY"

    def verify_document(
        self, document_number: str, nationality: str, document_type: str = "PASSPORT"
    ) -> Dict[str, Any]:
        clean_num = (document_number or "").replace(" ", "").upper()

        # Simulated test scenarios based on deterministic document number patterns
        if "REV" in clean_num or "STOLEN" in clean_num:
            return {
                "provider": self.PROVIDER_NAME,
                "status": "REVOKED",
                "is_mock": True,
                "reason": "Document reported stolen / cancelled in test registry database",
                "registry_record_id": f"REC-REV-{clean_num}",
            }
        elif "EXP" in clean_num:
            return {
                "provider": self.PROVIDER_NAME,
                "status": "EXPIRED",
                "is_mock": True,
                "reason": "Document record is marked expired in mock registry",
                "registry_record_id": f"REC-EXP-{clean_num}",
            }
        elif "NOTFOUND" in clean_num or "MISSING" in clean_num:
            return {
                "provider": self.PROVIDER_NAME,
                "status": "NOT_FOUND",
                "is_mock": True,
                "reason": "No document record found with this identifier in test registry",
                "registry_record_id": None,
            }
        elif "TIMEOUT" in clean_num or "DOWN" in clean_num:
            return {
                "provider": self.PROVIDER_NAME,
                "status": "UNAVAILABLE",
                "is_mock": True,
                "reason": "Simulated external service timeout / registry network outage",
                "registry_record_id": None,
            }

        # Default valid test response
        return {
            "provider": self.PROVIDER_NAME,
            "status": "VALID",
            "is_mock": True,
            "reason": "Document record confirmed active in simulated test database",
            "registry_record_id": f"MOCK-REG-{clean_num}-ACTIVE",
        }


class AuthorizedGovernmentProvider(ExternalVerificationProvider):
    """Production government registry provider adapter with strict timeout and TLS handling."""

    PROVIDER_NAME = "GOV_REGISTRY_AUTHORIZED"

    def __init__(self, endpoint: str = "", api_key: str = "", timeout_seconds: float = 3.0):
        self.endpoint = endpoint
        self.api_key = api_key
        self.timeout = timeout_seconds

    def verify_document(
        self, document_number: str, nationality: str, document_type: str = "PASSPORT"
    ) -> Dict[str, Any]:
        if not self.endpoint:
            # If production endpoint is unconfigured, return UNAVAILABLE rather than failing silently
            return {
                "provider": self.PROVIDER_NAME,
                "status": "UNAVAILABLE",
                "is_mock": False,
                "reason": "Authorized government registry endpoint is not configured",
                "registry_record_id": None,
            }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(
                    f"{self.endpoint}/v1/verify",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "document_number": document_number,
                        "nationality": nationality,
                        "document_type": document_type,
                    },
                )
                if res.status_code == 200:
                    data = res.json()
                    return {
                        "provider": self.PROVIDER_NAME,
                        "status": data.get("status", "VALID"),
                        "is_mock": False,
                        "reason": data.get("message", "Verified against authorized registry"),
                        "registry_record_id": data.get("reference_id"),
                    }
                elif res.status_code == 404:
                    return {
                        "provider": self.PROVIDER_NAME,
                        "status": "NOT_FOUND",
                        "is_mock": False,
                        "reason": "Document not found in authorized government registry",
                        "registry_record_id": None,
                    }
                else:
                    return {
                        "provider": self.PROVIDER_NAME,
                        "status": "UNAVAILABLE",
                        "is_mock": False,
                        "reason": f"Registry upstream returned HTTP {res.status_code}",
                        "registry_record_id": None,
                    }
        except httpx.TimeoutException:
            # Crucial: UNAVAILABLE must never be converted to VALID or INVALID
            return {
                "provider": self.PROVIDER_NAME,
                "status": "UNAVAILABLE",
                "is_mock": False,
                "reason": "External government registry request timed out",
                "registry_record_id": None,
            }
        except Exception as e:
            return {
                "provider": self.PROVIDER_NAME,
                "status": "UNAVAILABLE",
                "is_mock": False,
                "reason": f"Connection to authorized registry failed: {str(e)}",
                "registry_record_id": None,
            }


def get_external_provider() -> ExternalVerificationProvider:
    """Factory selecting provider based on configuration."""
    if settings.EXTERNAL_REGISTRY_PROVIDER == "authorized":
        return AuthorizedGovernmentProvider()
    return MockRegistryProvider()
