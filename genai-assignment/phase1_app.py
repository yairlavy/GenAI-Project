import streamlit as st
import tempfile
import json
import base64
from pathlib import Path

from phase1.pipeline import process_file


# Configure basic page settings such as title and layout.
# We use a centered layout to keep the UI focused and professional.
st.set_page_config(
    page_title="National Insurance Form Extraction",
    layout="centered",
    initial_sidebar_state="collapsed"
)


def apply_background_image():
    """
    Applies a full-screen background image using CSS.
    Updated to use the .stApp selector for better stability.
    """
    # Resolve absolute path to image to avoid "File not found" errors
    current_dir = Path(__file__).parent.resolve()
    background_path = current_dir / "UI" / "background.png"
    
    encoded_image = ""

    if background_path.exists():
        encoded_image = base64.b64encode(
            background_path.read_bytes()
        ).decode()
    else:
        st.warning(f"Background image not found at: {background_path}")

    st.markdown(
        f"""
        <style>
        /* General font settings */
        html, body, [class*="css"] {{
            font-family: "Segoe UI", sans-serif;
        }}

        /* Apply background to the main app container */
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_image}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}

        /* Make the content container semi-transparent white */
        /* This ensures text is readable against the background */
        .block-container {{
            background-color: rgba(255, 255, 255, 0.95);
            padding: 3rem;
            border-radius: 14px;
            max-width: 900px;
            margin: 3rem auto;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        }}

        /* Header styling */
        h1, h2 {{
            color: #1f2937;
            text-align: center;
        }}
        
        /* File uploader styling refinement */
        div[data-testid="stFileUploader"] {{
            margin-top: 1rem;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# Apply the background image as soon as the app loads.
apply_background_image()


# Main title of the application.
st.markdown(
    "<h1>National Insurance Form – Field Extraction</h1>",
    unsafe_allow_html=True
)

# Short explanation of what the tool does.
st.markdown(
    """
    <div style='text-align: center; color: #4b5563; margin-bottom: 20px;'>
    Upload a filled National Insurance (ביטוח לאומי) form in PDF format.<br>
    The system extracts structured information using OCR and Azure OpenAI
    and returns the data in a standardized JSON format.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<hr>", unsafe_allow_html=True)


# File uploader component.
# Only PDF files are allowed, as required by the assignment.
uploaded_file = st.file_uploader(
    "Upload PDF file",
    type=["pdf"]
)


if uploaded_file:
    st.success("File uploaded successfully")

    # Save the uploaded file to a temporary location
    # so it can be processed by the OCR and LLM pipeline.
    with st.spinner("Processing document..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.read())
            pdf_path = temp_file.name

        # Run the full processing pipeline:
        # OCR -> LLM extraction -> validation
        try:
            result = process_file(pdf_path)
            
            extracted_data = result["extracted_data"]
            validation_report = result["validation"]

            # Display extracted structured data.
            st.markdown("<h2>Extracted Data</h2>", unsafe_allow_html=True)
            st.json(extracted_data)

            # Allow the user to download the extracted JSON.
            st.download_button(
                label="Download Extracted JSON",
                data=json.dumps(extracted_data, ensure_ascii=False, indent=2),
                file_name="extracted_data.json",
                mime="application/json"
            )

            st.markdown("<hr>", unsafe_allow_html=True)

            # Display validation results, including completeness and missing fields.
            st.markdown("<h2>Validation Report</h2>", unsafe_allow_html=True)
            st.json(validation_report)

            # Allow the user to download the validation report as JSON.
            st.download_button(
                label="Download Validation Report",
                data=json.dumps(validation_report, ensure_ascii=False, indent=2),
                file_name="validation_report.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"An error occurred during processing: {e}")