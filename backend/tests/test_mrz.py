"""Tests for Module 3/6: ICAO 9303 MRZ Parsing and Checksum Validation."""

import pytest
from backend.app.modules.mrz import mrz_validator


def test_icao_9303_standard_passport_mrz():
    # Official ICAO 9303 Part 4 specimen TD3 MRZ
    line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
    line2 = "L898902C36UTO7408122F1204159ZE184226B<<<<<10"

    parsed = mrz_validator.parse_td3(line1, line2)

    assert parsed["status"] == "PASS"
    assert parsed["document_number"] == "L898902C3"
    assert parsed["surname"] == "ERIKSSON"
    assert parsed["given_names"] == "ANNA MARIA"
    assert parsed["nationality"] == "UTO"
    assert parsed["date_of_birth"] == "1974-08-12"
    assert parsed["sex"] == "F"
    assert parsed["checksums"]["document_number_valid"] is True
    assert parsed["checksums"]["dob_valid"] is True
    assert parsed["checksums"]["all_valid"] is True


def test_mrz_corrupted_checksum_detected():
    # Deliberately modify passport number digit to trigger checksum failure
    line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
    line2 = "L898902C39UTO7408122F1204159ZE184226B<<<<<10"  # '9' instead of correct check digit '6'

    parsed = mrz_validator.parse_td3(line1, line2)

    assert parsed["status"] == "INVALID"
    assert parsed["checksums"]["document_number_valid"] is False
    assert parsed["checksums"]["all_valid"] is False


def test_mrz_visual_cross_check_discrepancy():
    line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
    line2 = "L898902C36UTO7408122F1204159ZE184226B<<<<<10"
    mrz = mrz_validator.parse_td3(line1, line2)

    # Discrepant visual DOB (visual says 1974-08-15, MRZ says 1974-08-12)
    visual = {
        "document_number": {"value": "L898902C3"},
        "date_of_birth": {"value": "1974-08-15"},
        "nationality": {"value": "UTO"},
    }

    mismatches = mrz_validator.compare_with_visual(mrz, visual)
    assert len(mismatches) == 1
    assert mismatches[0]["field"] == "date_of_birth"
    assert "discrepancy" in mismatches[0]["explanation"].lower() or "mismatch" in mismatches[0]["explanation"].lower()
