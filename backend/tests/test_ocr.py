"""Tests for Module 3: OCR and Field Extraction."""

from backend.app.modules.ocr import ocr_engine


def test_ocr_field_parsing():
    sample_ocr_text = """
    PASSPORT / PASSEPORT
    SURNAME: ERIKSSON
    NAME: ANNA MARIA
    NATIONALITY: UTO
    DATE OF BIRTH: 12/08/1974
    SEX: F
    DOCUMENT NUMBER: L898902C3
    EXPIRY DATE: 15/04/2030
    """

    fields = ocr_engine.parse_fields_from_text(sample_ocr_text)

    assert "document_number" in fields
    assert fields["document_number"]["value"] == "L898902C3"

    assert "nationality" in fields
    assert fields["nationality"]["value"] == "UTO"

    assert "date_of_birth" in fields
    assert fields["date_of_birth"]["value"] == "1974-08-12"

    assert "expiry_date" in fields
    assert fields["expiry_date"]["value"] == "2030-04-15"

    assert "name" in fields
    assert "ERIKSSON" in fields["name"]["value"]
