"""Module 3/6: ICAO 9303 Machine Readable Zone (MRZ) Parser and Checksum Engine."""

import re
from typing import Dict, Any, List, Optional, Tuple


class MRZValidator:
    WEIGHTS = [7, 3, 1]

    @classmethod
    def char_to_value(cls, char: str) -> int:
        """Convert an ICAO MRZ character to its numerical value."""
        char = char.upper()
        if char == "<":
            return 0
        if char.isdigit():
            return int(char)
        if "A" <= char <= "Z":
            return ord(char) - ord("A") + 10
        return 0

    @classmethod
    def calculate_check_digit(cls, field_str: str) -> int:
        """Calculate ICAO 9303 mod-10 check digit with 7-3-1 weight progression."""
        total = 0
        for i, char in enumerate(field_str):
            weight = cls.WEIGHTS[i % 3]
            total += cls.char_to_value(char) * weight
        return total % 10

    @classmethod
    def verify_check_digit(cls, field_str: str, expected_digit: str) -> bool:
        if not expected_digit.isdigit():
            return False
        return cls.calculate_check_digit(field_str) == int(expected_digit)

    @classmethod
    def parse_td3(cls, line1: str, line2: str) -> Dict[str, Any]:
        """Parse standard 2x44 passport MRZ (ICAO 9303 TD3)."""
        line1 = line1.strip().upper()
        line2 = line2.strip().upper()

        if len(line1) != 44 or len(line2) != 44:
            raise ValueError(f"TD3 MRZ requires 44 chars per line (got {len(line1)} and {len(line2)})")

        doc_type = line1[0:2].replace("<", "")
        issuing_country = line1[2:5].replace("<", "")
        names_part = line1[5:44]

        # Extract Surname << Given Names
        name_tokens = names_part.split("<<")
        surname = name_tokens[0].replace("<", " ").strip()
        given_names = name_tokens[1].replace("<", " ").strip() if len(name_tokens) > 1 else ""
        full_name = f"{given_names} {surname}".strip()

        # Line 2 components
        doc_num = line2[0:9].replace("<", "")
        doc_num_check = line2[9]
        nationality = line2[10:13].replace("<", "")
        dob_raw = line2[13:19]
        dob_check = line2[19]
        sex = line2[20].replace("<", "X")
        expiry_raw = line2[21:27]
        expiry_check = line2[27]
        personal_num = line2[28:42].replace("<", "")
        personal_check = line2[42]
        composite_check = line2[43]

        # Checksum validations
        doc_num_valid = cls.verify_check_digit(line2[0:9], doc_num_check)
        dob_valid = cls.verify_check_digit(dob_raw, dob_check)
        expiry_valid = cls.verify_check_digit(expiry_raw, expiry_check)

        # Composite verification string: line2[0:10] + line2[13:20] + line2[21:43]
        composite_str = line2[0:10] + line2[13:20] + line2[21:43]
        composite_valid = cls.verify_check_digit(composite_str, composite_check)

        # Parse ISO dates (YYMMDD to YYYY-MM-DD)
        dob_iso = cls._parse_mrz_date(dob_raw, is_birth=True)
        expiry_iso = cls._parse_mrz_date(expiry_raw, is_birth=False)

        all_valid = doc_num_valid and dob_valid and expiry_valid and composite_valid

        return {
            "format": "TD3",
            "document_type": doc_type or "PASSPORT",
            "issuing_country": issuing_country,
            "surname": surname,
            "given_names": given_names,
            "full_name": full_name,
            "document_number": doc_num,
            "nationality": nationality,
            "date_of_birth": dob_iso,
            "sex": sex,
            "expiry_date": expiry_iso,
            "personal_number": personal_num,
            "checksums": {
                "document_number_valid": doc_num_valid,
                "dob_valid": dob_valid,
                "expiry_valid": expiry_valid,
                "composite_valid": composite_valid,
                "all_valid": all_valid,
            },
            "status": "PASS" if all_valid else "INVALID",
        }

    @classmethod
    def _parse_mrz_date(cls, yymmdd: str, is_birth: bool = False) -> str:
        """Convert YYMMDD to YYYY-MM-DD."""
        if len(yymmdd) != 6 or not yymmdd.isdigit():
            return yymmdd
        yy = int(yymmdd[0:2])
        mm = yymmdd[2:4]
        dd = yymmdd[4:6]

        current_year_short = int(str(2026)[2:4])
        if is_birth:
            # If yy <= current_year_short, likely 2000s; otherwise 1900s
            century = 2000 if yy <= current_year_short else 1900
        else:
            # Expiry dates: if yy < 70 likely 2000s
            century = 2000 if yy < 70 else 1900

        full_year = century + yy
        return f"{full_year}-{mm}-{dd}"

    @classmethod
    def compare_with_visual(
        cls, mrz_data: Dict[str, Any], visual_fields: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Compare parsed MRZ data against visual OCR fields and return discrepancies."""
        mismatches: List[Dict[str, Any]] = []

        # 1. Document number check
        if "document_number" in visual_fields:
            v_val = visual_fields["document_number"]["value"].replace(" ", "").upper()
            m_val = mrz_data.get("document_number", "").replace(" ", "").upper()
            if v_val and m_val and v_val != m_val:
                mismatches.append({
                    "field": "document_number",
                    "visual": v_val,
                    "mrz": m_val,
                    "explanation": f"Document number discrepancy: Visual ({v_val}) differs from MRZ ({m_val})",
                })

        # 2. Date of birth check
        if "date_of_birth" in visual_fields:
            v_val = visual_fields["date_of_birth"]["value"]
            m_val = mrz_data.get("date_of_birth", "")
            if v_val and m_val and v_val != m_val:
                mismatches.append({
                    "field": "date_of_birth",
                    "visual": v_val,
                    "mrz": m_val,
                    "explanation": f"Date of birth mismatch: Visual ({v_val}) differs from MRZ ({m_val})",
                })

        # 3. Expiry date check
        if "expiry_date" in visual_fields:
            v_val = visual_fields["expiry_date"]["value"]
            m_val = mrz_data.get("expiry_date", "")
            if v_val and m_val and v_val != m_val:
                mismatches.append({
                    "field": "expiry_date",
                    "visual": v_val,
                    "mrz": m_val,
                    "explanation": f"Expiry date mismatch: Visual ({v_val}) differs from MRZ ({m_val})",
                })

        # 4. Nationality check
        if "nationality" in visual_fields:
            v_val = visual_fields["nationality"]["value"].upper()
            m_val = mrz_data.get("nationality", "").upper()
            if v_val and m_val and v_val != m_val:
                mismatches.append({
                    "field": "nationality",
                    "visual": v_val,
                    "mrz": m_val,
                    "explanation": f"Nationality mismatch: Visual ({v_val}) differs from MRZ ({m_val})",
                })

        return mismatches


mrz_validator = MRZValidator()
