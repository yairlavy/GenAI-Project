import json
from typing import Dict, Any
from phase2.llm_client import call_llm
from phase2.schemas import UserProfile

def user_info_extraction_prompt(language: str) -> str:
    """
    Returns the specific prompt for the extractor based on language.
    """
    if language == "en":
        return """
        You are an information extraction engine.
        Extract user details from the user's message into a valid JSON object.
        
        Target JSON Format:
        {
            "first_name": "...", "last_name": "...", "id_number": "...",
            "gender": "...", "age": 123, "hmo": "...",
            "hmo_card_number": "...", "insurance_tier": "..."
        }
        
        Rules:
        1. Only include fields that are explicitly mentioned.
        2. Return ONLY the JSON object. No markdown.
        3. Map values to English or Hebrew as appropriate, but keep them consistent.
        """
    else:
        return """
        אתה מנוע לחילוץ מידע.
        חלץ פרטי משתמש מתוך ההודעה לפורמט JSON תקין.
        
        פורמט יעד:
        {
            "first_name": "...", "last_name": "...", "id_number": "...",
            "gender": "...", "age": 123, "hmo": "...",
            "hmo_card_number": "...", "insurance_tier": "..."
        }
        
        כללים:
        1. כלול רק שדות שהוזכרו במפורש.
        2. החזר רק את ה-JSON. ללא מרקדאון.
        """

def extract_user_info(message: str, language: str) -> Dict[str, Any]:
    """
    Extracts structured user information from a single user message.
    """
    system_prompt = user_info_extraction_prompt(language)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"User message:\n{message}"}
    ]

    response = call_llm(messages)

    try:
        # Clean markdown if present
        text = response.replace("```json", "").replace("```", "").strip()
        extracted = json.loads(text)
    except json.JSONDecodeError:
        return {}

    if not isinstance(extracted, dict):
        return {}

    # Allow known UserProfile fields
    allowed_fields = set(UserProfile.model_fields.keys())
    cleaned: Dict[str, Any] = {}

    for field, value in extracted.items():
        if field not in allowed_fields:
            continue
        if value in ("", None):
            continue
            
        # Basic validation (can be expanded)
        if field == "id_number" and not (str(value).isdigit() and len(str(value)) == 9):
            continue
        if field == "age" and not (isinstance(value, int) and 0 <= value <= 120):
            continue
        
        cleaned[field] = value

    return cleaned