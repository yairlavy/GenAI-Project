from pathlib import Path
import json

from phase1.ocr import extract_text_from_file
from phase1.llm_extractor import extract_fields_with_llm
from phase1.validator import validate_extraction


def process_file(file_path: str) -> dict:
    """
    Full processing pipeline:
    - OCR
    - LLM extraction
    - Validation

    Returns a dict with both extracted data and validation report.
    """

    ocr_text = extract_text_from_file(file_path)
    extracted_data = extract_fields_with_llm(ocr_text)
    validation_report = validate_extraction(extracted_data)

    return {
        "extracted_data": extracted_data,
        "validation": validation_report
    }


if __name__ == "__main__":
    current_dir = Path(__file__).parent
    pdf_path = (
        current_dir / ".." / "phase1_data" / "283_ex1.pdf"
    ).resolve()

    result = process_file(str(pdf_path))

    print("----- FINAL EXTRACTED JSON -----")
    print(json.dumps(result["extracted_data"], ensure_ascii=False, indent=2))

    print("----- VALIDATION REPORT -----")
    print(json.dumps(result["validation"], ensure_ascii=False, indent=2))
