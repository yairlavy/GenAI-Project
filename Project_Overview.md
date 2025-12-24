**GenAI Developer Assessment: Intelligent Form Extraction & Medical Chatbot
**
Project Overview

This project is a comprehensive Generative AI solution designed to automate administrative tasks and provide intelligent medical assistance. It leverages Azure OpenAI (GPT-4o & Ada-002) and Azure Document Intelligence to solve two distinct real-world challenges:

**Intelligent Form Extraction
**
An automated pipeline that converts complex National Insurance (Bituach Leumi) PDF forms—containing handwriting and checkboxes—into structured, validated JSON data.

**Medical Services Chatbot
**
A secure, stateless RAG (Retrieval-Augmented Generation) chatbot that answers questions about Israeli Health Funds. It uses vector search to retrieve accurate information and avoids hallucinations.

**Prerequisites
**
Before running the project, ensure you have the following installed:
Python 3.10 or higher
Git (optional, for cloning the repository)

Azure Credentials:
Azure OpenAI Endpoint & API Key
Azure Document Intelligence Endpoint & API Key


Installation & Setup
1. Set Up a Virtual Environment

# Create virtual environment
python -m venv .venv

# Activate the environment
# Windows
.venv\Scripts\activate

# Mac / Linux
source .venv/bin/activate

Install Dependencies
Install all required Python libraries using the requirements file:

bash
pip install -r requirements.txt

Configure Environment Variables
Create a .env file in the project root and add your Azure credentials:

AZURE_OPENAI_ENDPOINT="your_openai_endpoint"
AZURE_OPENAI_KEY="your_openai_key"
AZURE_DI_ENDPOINT="your_document_intelligence_endpoint"
AZURE_DI_KEY="your_document_intelligence_key"

How to Run the System

You can run the system automatically (Windows) or manually.

Option A: Automatic Launch (Windows)
Double-click Launcher.bat in the root directory.
The script will:

Activate the virtual environment
Install missing dependencies
Launch the Backend API and both Streamlit UIs in separate windows

Option B: Manual Launch (Step-by-Step)

You will need three terminal windows.
Ensure the virtual environment is activated in all of them.

Terminal 1: Backend API (Phase 2 – Server)
Runs the chatbot backend.

uvicorn phase2.api:app --reload

Keep this window open.

Terminal 2: Phase 1 UI – Form Extraction
streamlit run phase1_app.py

Terminal 3: Phase 2 UI – Medical Chatbot
streamlit run phase2_app.py

Phase 1: Intelligent Form Extraction

The Challenge: Extracting data from Form 283 (Bituach Leumi) is challenging because Standard OCR fails with checkboxes (checked vs unchecked) Handwriting lacks clear context

The Solution: Smart OCR Pipeline
Smart OCR (ocr.py)

Uses Azure Document Intelligence’s prebuilt-layout model.
Instead of only extracting text, the pipeline iterates over detected selection_marks and patches the text:

[X] for checked boxes
[ ] for unchecked boxes

LLM Extraction (llm_extractor.py)

The processed text is sent to GPT-4o with a strict system prompt that enforces output according to a predefined JSON schema (schemas.py).

Validation Layer (validator.py)
Validation is done using Pydantic, checking:
Logical consistency (IDs, dates)
Data completeness (fill-rate score)
Correct data types (int vs string)

Phase 2: Medical Services Chatbot

The Challenge: Provide accurate medical information while:
Preventing hallucinations
Avoiding server-side memory storage
Scaling safely

The Solution: Stateless RAG Architecture
Stateless Microservice (api.py)

Built with FastAPI.
The server stores no session state.
The client (Streamlit) sends the full conversation and user profile on every request.

Vector Search / RAG (knowledge_loader.py)
Chunking: HTML files are split into logical text chunks
Embeddings: Ada-002 converts chunks into vectors
Retrieval: Cosine similarity selects the top 3 relevant chunks
Generation: Only retrieved context is sent to GPT-4o

Security & Prompt Injection Protection

System context is injected using XML tags (e.g., <user_context>), clearly separating trusted system data from user input.
Developer Experience (logger.py)
Centralized logging system
Logs written to logs/chatbot.log

Developer Sidebar Feature
The UI displays backend logs in real time, exposing the model’s reasoning and retrieval process live.

Project Structure

It is recommended to use a virtual environment to isolate dependencies
genai-assignment/
├── phase1/                 # Logic for Form Extraction
│   ├── ocr.py              # Smart OCR implementation
│   ├── llm_extractor.py    # GPT-4o extraction logic
│   └── validator.py        # Pydantic validation rules
├── phase2/                 # Logic for Chatbot Microservice
│   ├── api.py              # FastAPI Backend Entry Point
│   ├── knowledge_loader.py # RAG & Vector Store logic
│   ├── llm_client.py       # Azure OpenAI wrapper (Chat & Embeddings)
│   ├── logger.py           # Centralized logging system
│   └── prompts.py          # System prompts storage
├── UI/                     # Assets (Background images)
├── phase1_app.py           # Streamlit Frontend for Phase 1
├── phase2_app.py           # Streamlit Frontend for Phase 2
├── Launcher.bat            # Auto-start script
└── requirements.txt        # Python dependencies
