import os
import json
from dotenv import load_dotenv

from openai import AzureOpenAI
from phase1.schemas import InjuryFormModel


# Load environment variables from the .env file
# This allows us to access the Azure OpenAI endpoint and key
load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")

if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_KEY:
    raise RuntimeError("Missing AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_KEY")


# Create a client that can communicate with Azure OpenAI
# This client will be reused every time we want to call GPT
client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version="2024-02-15-preview"
)


def extract_fields_with_llm(ocr_text: str) -> dict:
    """
    Receives raw OCR text extracted from a document.
    Sends the text to GPT with very strict instructions.
    Returns a Python dictionary that matches InjuryFormModel.
    """

    # We explicitly describe the task to the model.
    # The model is not allowed to guess or add information.
    system_prompt = (
        "You are an information extraction engine.\n"
        "Your task is to extract structured data from OCR text of a National Insurance form.\n"
        "Do not add information that does not appear in the text.\n"
        "If a field is missing or unclear, return an empty string.\n"
        "Return only valid JSON. Do not include explanations or extra text."
    )

    # We provide the OCR text and clearly describe the expected output structure.
    # The JSON structure must match the InjuryFormModel exactly.
    user_prompt = f"""
Extract the following OCR text into the exact JSON structure below.

OCR TEXT:
\"\"\"
{ocr_text}
\"\"\"

JSON STRUCTURE:
{json.dumps(InjuryFormModel().model_dump(), ensure_ascii=False, indent=2)}

Rules:
- Return ONLY JSON
- Keep all keys exactly as shown
- Use empty strings ("") for missing values
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

    # The model should return JSON only, but we still parse it safely
    try:
        extracted_data = json.loads(raw_content)
    except json.JSONDecodeError as e:
        raise ValueError("LLM response is not valid JSON") from e

    return extracted_data


if __name__ == "__main__":
    # This is a manual test to verify that the LLM extraction works.
    # It uses OCR output text saved from a previous OCR run.

    sample_text = """
    שם משפחה טננהוים
    שם פרטי יהודה
    ת.ז. 877524563
    מין זכר
    תאריך לידה 02.02.1995
    """

    extracted = extract_fields_with_llm(sample_text)

    print("Extracted JSON:")
    print(json.dumps(extracted, ensure_ascii=False, indent=2))
