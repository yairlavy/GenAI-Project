import re
from typing import Any, Dict, List, Tuple

from phase1.schemas import InjuryFormModel


def _is_empty(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def _flatten_fields(data: Dict[str, Any], prefix: str = "") -> List[Tuple[str, Any]]:
    """
    Turns nested dict into a flat list of (field_path, value).
    Example: {"address": {"city": "X"}} -> [("address.city", "X")]
    """
    items: List[Tuple[str, Any]] = []
    for k, v in data.items():
        path = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            items.extend(_flatten_fields(v, path))
        else:
            items.append((path, v))
    return items


def _validate_date(date_obj: Dict[str, Any], field_name: str) -> List[str]:
    """
    Validates a date structure {day, month, year}.
    Does not "fix" values; only reports problems.
    """
    errors: List[str] = []

    day = (date_obj.get("day") or "").strip()
    month = (date_obj.get("month") or "").strip()
    year = (date_obj.get("year") or "").strip()

    if _is_empty(day) and _is_empty(month) and _is_empty(year):
        return errors  # empty date is allowed (will be counted as missing/completeness)

    if not re.fullmatch(r"\d{1,2}", day):
        errors.append(f"{field_name}.day should be 1-2 digits or empty")
    if not re.fullmatch(r"\d{1,2}", month):
        errors.append(f"{field_name}.month should be 1-2 digits or empty")
    if not re.fullmatch(r"\d{4}", year):
        errors.append(f"{field_name}.year should be 4 digits or empty")

    # Range checks only if numeric
    try:
        if day and not (1 <= int(day) <= 31):
            errors.append(f"{field_name}.day out of range (1-31)")
    except ValueError:
        pass
    try:
        if month and not (1 <= int(month) <= 12):
            errors.append(f"{field_name}.month out of range (1-12)")
    except ValueError:
        pass

    return errors


def validate_extraction(extracted: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates the extracted JSON.
    Important: this function does NOT change the extracted data.
    It only reports errors/warnings and completeness.
    """

    report = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "completeness": 0.0,
        "missing_fields": []
    }

    # 1) Schema validation (structure)
    # If the dict cannot fit the model structure, this is a hard error.
    try:
        model = InjuryFormModel.model_validate(extracted)
        data = model.model_dump()
    except Exception as e:
        report["is_valid"] = False
        report["errors"].append(f"Schema validation failed: {str(e)}")
        return report

    # 2) Completeness calculation (how many leaf fields are filled)
    flat = _flatten_fields(data)
    total_fields = len(flat)
    filled_fields = sum(0 if _is_empty(v) else 1 for _, v in flat)

    report["completeness"] = round(filled_fields / total_fields, 3)

    for path, value in flat:
        if _is_empty(value):
            report["missing_fields"].append(path)

    # 3) Basic field checks (examples that match the spec)
    # We do not correct; we only warn/error.

    # ID number: should be 9 digits (requirement in Part 2, but still useful here)
    id_number = (data.get("idNumber") or "").strip()
    if id_number:
        if not re.fullmatch(r"\d+", id_number):
            report["warnings"].append("idNumber contains non-digit characters")
        elif len(id_number) != 9:
            report["warnings"].append(f"idNumber length is {len(id_number)} (expected 9 digits)")

    # Gender: should be a known value if present
    gender = (data.get("gender") or "").strip()
    if gender and gender not in ["זכר", "נקבה", "male", "female", "M", "F"]:
        report["warnings"].append(f"gender value looks unusual: '{gender}'")

    # Phone numbers: digit-only check (light warning)
    mobile = (data.get("mobilePhone") or "").strip()
    if mobile and not re.fullmatch(r"\d{7,15}", mobile):
        report["warnings"].append("mobilePhone format looks unusual (expected 7-15 digits)")

    landline = (data.get("landlinePhone") or "").strip()
    if landline and not re.fullmatch(r"\d{7,15}", landline):
        report["warnings"].append("landlinePhone format looks unusual (expected 7-15 digits)")

    # Date fields validation (structure + range checks)
    report["warnings"].extend(_validate_date(data.get("dateOfBirth", {}), "dateOfBirth"))
    report["warnings"].extend(_validate_date(data.get("dateOfInjury", {}), "dateOfInjury"))
    report["warnings"].extend(_validate_date(data.get("formFillingDate", {}), "formFillingDate"))
    report["warnings"].extend(_validate_date(data.get("formReceiptDateAtClinic", {}), "formReceiptDateAtClinic"))

    # 4) Decide is_valid
    # Hard errors would be in report["errors"].
    # Warnings do not fail the run.
    if report["errors"]:
        report["is_valid"] = False

    return report
