import os
import json
import re
from dotenv import load_dotenv
from openai import AzureOpenAI
from phase1.schemas import InjuryFormModel

# Load environment variables
load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")

if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_KEY:
    raise RuntimeError("Missing Azure OpenAI credentials")

client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version="2024-02-15-preview"
)

def clean_json_string(text: str) -> str:
    """
    Helper function to strip Markdown code blocks (```json ... ```)
    from the LLM response so json.loads doesn't crash.
    """
    # Remove ```json wrapper if it exists
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    # Remove generic ``` wrapper if it exists
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    
    return text.strip()

def extract_fields_with_llm(ocr_text: str) -> dict:
    """
    Receives raw OCR text, sends it to GPT-4o, and returns a clean dictionary.
    """
    
    system_prompt = (
        "You are an information extraction engine.\n"
        "Your task is to extract structured data from OCR text of a National Insurance form.\n"
        "Do not add information that does not appear in the text.\n"
        "If a field is missing or unclear, return an empty string.\n"
        "Return only valid JSON. Do not include explanations or extra text."
    )

    # Convert the Pydantic model to a JSON schema example
    # so the LLM knows exactly what format to output.
    json_structure = json.dumps(InjuryFormModel().model_dump(), ensure_ascii=False, indent=2)

    user_prompt = f"""
Extract the following OCR text into the exact JSON structure below.

OCR TEXT:
\"\"\"
{ocr_text}
\"\"\"

JSON STRUCTURE:
{json_structure}

Rules:
- Return ONLY JSON
- Keep all keys exactly as shown
- Use empty strings ("") for missing values
- Treat '[X]' as a selected checkbox (True/Yes)
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0
    )

    raw_content = response.choices[0].message.content

    # FIX: Clean the response before parsing
    cleaned_content = clean_json_string(raw_content)

    try:
        extracted_data = json.loads(cleaned_content)
    except json.JSONDecodeError as e:
        print(f"FAILED TO PARSE JSON. Raw content:\n{raw_content}")
        raise ValueError("LLM response is not valid JSON") from e

    return extracted_data

if __name__ == "__main__":
    # Test block
    sample_text = """
    שם משפחה טננהוים
    שם פרטי יהודה
    ת.ז. 877524563
    מין זכר
    """
    try:
        extracted = extract_fields_with_llm(sample_text)
        print("Extracted JSON:")
        print(json.dumps(extracted, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {e}")