import json
from typing import Dict, Any

from phase2.prompts import user_info_extraction_prompt
from phase2.llm_client import call_llm
from phase2.schemas import UserProfile


def extract_user_info(
    message: str,
    language: str,
) -> Dict[str, Any]:
    """
    Extracts structured user information from a single user message.
    """

    system_prompt = user_info_extraction_prompt(language)

    # Format messages as a list of dictionaries with roles
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"User message:\n{message}"}
    ]

    response = call_llm(messages)

    try:
        extracted = json.loads(response)
    except json.JSONDecodeError:
        return {}

    if not isinstance(extracted, dict):
        return {}

    # Allow only known UserProfile fields
    allowed_fields = set(UserProfile.model_fields.keys())

    cleaned: Dict[str, Any] = {}

    for field, value in extracted.items():
        if field not in allowed_fields:
            continue

        if value in ("", None):
            continue
            
        if field == "id_number" and not (isinstance(value, str) and value.isdigit() and len(value) == 9):
            continue

        if field == "age" and not (isinstance(value, int) and 0 <= value <= 120):
            continue
        
        cleaned[field] = value

    return cleaned