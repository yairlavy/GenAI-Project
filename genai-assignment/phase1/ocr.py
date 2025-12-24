import os
from dotenv import load_dotenv
from pathlib import Path

# Azure SDK imports for Document Intelligence (OCR)
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables from .env file
# This allows us to keep secrets (keys, endpoints)
# outside of the code.
load_dotenv()

# Read Azure Document Intelligence credentials
DI_ENDPOINT = os.getenv("AZURE_DI_ENDPOINT")
DI_KEY = os.getenv("AZURE_DI_KEY")

# Safety check: if credentials are missing, stop immediately
if not DI_ENDPOINT or not DI_KEY:
    raise RuntimeError("Missing AZURE_DI_ENDPOINT or AZURE_DI_KEY in .env file")


# Main OCR function
def extract_text_from_file(file_path: str) -> str:
    """
    Receives a path to a PDF or image file.
    Sends it to Azure Document Intelligence (OCR).
    Returns the full text with visual indicators for checkboxes ([X] / [ ]).
    """

    # Create a client that knows how to talk to Azure OCR service
    client = DocumentIntelligenceClient(
        endpoint=DI_ENDPOINT,
        credential=AzureKeyCredential(DI_KEY)
    )

    # Open the file in binary mode (required for PDFs and images)
    with open(file_path, "rb") as file:
        # Send the document to Azure for OCR analysis
        # 'prebuilt-layout' is a general OCR model that detects text and selection marks
        poller = client.begin_analyze_document(
            model_id="prebuilt-layout",
            body=file
        )

    # Wait for Azure to finish processing and return the result
    result = poller.result()

    # If no content was detected, return empty string
    if not result.content:
        return ""

    # Convert the full text content into a mutable list of characters.
    # This allows us to "patch" the text with checkbox statuses.
    text_chars = list(result.content)
    
    # Collect all selection marks from all pages
    all_marks = []
    if result.pages:
        for page in result.pages:
            if page.selection_marks:
                all_marks.extend(page.selection_marks)

    # Sort marks by their position (offset) in reverse order.
    # We process in reverse so that replacing text doesn't shift the indices 
    # of the marks we haven't processed yet.
    all_marks.sort(key=lambda x: x.span.offset, reverse=True)

    # Iterate through marks and inject visual cues into the text
    for mark in all_marks:
        # Determine the symbol: [X] for selected, [ ] for unselected
        symbol = "[X] " if mark.state == "selected" else "[ ] "
        
        start_index = mark.span.offset
        length = mark.span.length
        
        # Replace the original placeholder characters (often just space or garbage)
        # with our clear visual symbol.
        text_chars[start_index : start_index + length] = list(symbol)

    # Join the modified characters back into a single string
    full_text = "".join(text_chars)

    return full_text

if __name__ == "__main__":
    # Get the directory where THIS file (ocr.py) is located
    current_file_dir = Path(__file__).parent

    # Go one level up (to genai-assignment),
    # then into phase1_data
    pdf_path = (
        current_file_dir
        / ".."
        / "phase1_data"
        / "283_ex1.pdf"
    ).resolve()

    extracted_text = extract_text_from_file(str(pdf_path))

    print("PDF path used:")
    print(pdf_path)
    print("SMART OCR  ALL OUTPUT ")
    print(extracted_text[:1500]) # Print only the first 1500 characters