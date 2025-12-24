# GenAI Project: Intelligent Form Extraction & Medical Chatbot

This project presents an End-to-End solution based on Azure OpenAI and Azure Document Intelligence. The system is divided into two main parts:
1. **Phase 1:** An automated system for extracting structured data from National Insurance forms (handling handwriting and checkboxes).
2. **Phase 2:** A medical chatbot (RAG) that answers questions about Health Funds, designed as a stateless microservice.

## Setup & Installation

### 1. Prerequisites
* Python 3.10 or higher.
* Access keys for Azure OpenAI and Azure Document Intelligence.

### 2. Environment Setup
Open a terminal in the root directory and run:

```bash
# Create virtual environment
python -m venv .venv

# Activate environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

Environment Variables
Create a file named .env in the root directory and add your keys:

AZURE_OPENAI_ENDPOINT="your_endpoint"
AZURE_OPENAI_KEY="your_key"
AZURE_DI_ENDPOINT="your_ocr_endpoint"
AZURE_DI_KEY="your_ocr_key"

How to Run
Option A - Automatic Launch (Recommended for Windows)
Simply double-click the Launcher.bat file. It will automatically install dependencies and open the server and both user interfaces.

Option B - Manual Launch
You need to open 3 separate terminal windows (ensure the virtual environment is activated in all):

Terminal 1: Backend Server (Chatbot Brain)
uvicorn phase2.api:app --reload

Terminal 2: Form Analysis UI (Phase 1)
streamlit run phase1_app.py

Terminal 3: Chatbot UI (Phase 2)
streamlit run phase2_app.py
