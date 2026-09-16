"""Module 4: Versioned Deterministic Rules Engine."""

from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional


class RuleEngine:
    VERSION = "ruleset-v1.0"

    def __init__(self):
        pass

    def evaluate(self, canonical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all deterministic validation rules against canonical document data."""
        results: List[Dict[str, Any]] = []
        evidence_flags: List[Dict[str, Any]] = []

        # 1. Required Fields Check
        required_fields = ["name", "document_number", "nationality", "date_of_birth", "expiry_date"]
        missing_fields = [f for f in required_fields if not canonical_data.get(f)]

        if missing_fields:
            status = "FAIL"
            msg = f"Missing required document fields: {', '.join(missing_fields)}"
            evidence_flags.append({
                "category": "RULE_MISMATCH",
                "severity": "CRITICAL",
                "explanation": msg,
                "source_module": "rules_engine",
            })
        else:
            status = "PASS"
            msg = "All required identity fields present"

        results.append({
            "check_name": "REQUIRED_FIELDS",
            "status": status,
            "evidence": {"missing": missing_fields, "message": msg},
            "ruleset_version": self.VERSION,
        })

        # 2. Expiry Date Check
        expiry_raw = canonical_data.get("expiry_date")
        if expiry_raw:
            exp_date = self._parse_date(expiry_raw)
            today = datetime.now(timezone.utc).date()
            if exp_date:
                if exp_date < today:
                    results.append({
                        "check_name": "EXPIRY_CHECK",
                        "status": "FAIL",
                        "evidence": {"expiry_date": str(exp_date), "today": str(today), "message": "Document is expired"},
                        "ruleset_version": self.VERSION,
                    })
                    evidence_flags.append({
                        "category": "RULE_MISMATCH",
                        "severity": "CRITICAL",
                        "explanation": f"Document expired on {exp_date} (inspection date {today})",
                        "source_module": "rules_engine",
                    })
                else:
                    results.append({
                        "check_name": "EXPIRY_CHECK",
                        "status": "PASS",
                        "evidence": {"expiry_date": str(exp_date), "message": "Document is currently valid"},
                        "ruleset_version": self.VERSION,
                    })
            else:
                results.append({
                    "check_name": "EXPIRY_CHECK",
                    "status": "REVIEW",
                    "evidence": {"message": f"Malformed expiry date: {expiry_raw}"},
                    "ruleset_version": self.VERSION,
                })

        # 3. Document Number Format Check
        doc_num = canonical_data.get("document_number", "")
        if doc_num:
            clean_num = doc_num.replace(" ", "").upper()
            is_valid_format = clean_num.isalnum() and 6 <= len(clean_num) <= 12
            if not is_valid_format:
                results.append({
                    "check_name": "DOCUMENT_NUMBER_FORMAT",
                    "status": "FAIL",
                    "evidence": {"document_number": doc_num, "message": "Document number does not match standard 6-12 alphanumeric format"},
                    "ruleset_version": self.VERSION,
                })
                evidence_flags.append({
                    "category": "RULE_MISMATCH",
                    "severity": "WARNING",
                    "explanation": f"Irregular document number format: '{doc_num}'",
                    "source_module": "rules_engine",
                })
            else:
                results.append({
                    "check_name": "DOCUMENT_NUMBER_FORMAT",
                    "status": "PASS",
                    "evidence": {"document_number": doc_num, "message": "Format matches standard specification"},
                    "ruleset_version": self.VERSION,
                })

        # 4. Cross-Field Date Consistency Checks
        dob_raw = canonical_data.get("date_of_birth")
        if dob_raw and expiry_raw:
            dob = self._parse_date(dob_raw)
            exp = self._parse_date(expiry_raw)
            today = datetime.now(timezone.utc).date()

            if dob and exp:
                # Age calculation
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                if age < 0:
                    results.append({
                        "check_name": "DOB_LOGIC_CHECK",
                        "status": "FAIL",
                        "evidence": {"dob": str(dob), "message": "Date of birth is in the future"},
                        "ruleset_version": self.VERSION,
                    })
                    evidence_flags.append({
                        "category": "RULE_MISMATCH",
                        "severity": "CRITICAL",
                        "explanation": f"Date of birth ({dob}) is in the future",
                        "source_module": "rules_engine",
                    })
                elif age > 115:
                    results.append({
                        "check_name": "DOB_LOGIC_CHECK",
                        "status": "REVIEW",
                        "evidence": {"dob": str(dob), "calculated_age": age, "message": "Calculated age exceeds 115 years"},
                        "ruleset_version": self.VERSION,
                    })
                    evidence_flags.append({
                        "category": "RULE_MISMATCH",
                        "severity": "WARNING",
                        "explanation": f"Calculated age ({age} years) warrants manual inspection",
                        "source_module": "rules_engine",
                    })
                else:
                    results.append({
                        "check_name": "DOB_LOGIC_CHECK",
                        "status": "PASS",
                        "evidence": {"dob": str(dob), "age": age, "message": "Date of birth is chronologically consistent"},
                        "ruleset_version": self.VERSION,
                    })

                # Expiry must be after DOB
                if exp <= dob:
                    results.append({
                        "check_name": "EXPIRY_AFTER_DOB",
                        "status": "FAIL",
                        "evidence": {"dob": str(dob), "expiry": str(exp), "message": "Expiry date precedes or matches date of birth"},
                        "ruleset_version": self.VERSION,
                    })
                    evidence_flags.append({
                        "category": "RULE_MISMATCH",
                        "severity": "CRITICAL",
                        "explanation": f"Chronological anomaly: Expiry date ({exp}) is on or before date of birth ({dob})",
                        "source_module": "rules_engine",
                    })

        all_passed = all(r["status"] == "PASS" for r in results)
        any_failed = any(r["status"] == "FAIL" for r in results)
        overall_status = "FAIL" if any_failed else ("PASS" if all_passed else "REVIEW")

        return {
            "overall_status": overall_status,
            "ruleset_version": self.VERSION,
            "validation_results": results,
            "evidence_items": evidence_flags,
        }

    def _parse_date(self, val: Any) -> Optional[date]:
        if isinstance(val, date):
            return val
        if isinstance(val, datetime):
            return val.date()
        if not isinstance(val, str):
            return None
        val = val.strip().replace("/", "-").replace(".", "-")
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y%m%d"):
            try:
                return datetime.strptime(val, fmt).date()
            except ValueError:
                continue
        return None


rules_engine = RuleEngine()
