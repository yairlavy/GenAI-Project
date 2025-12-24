@echo off
echo Starting GenAI Assignment...

call .venv\Scripts\activate
call pip install -r requirements.txt

start cmd /k "uvicorn phase2.api:app --reload"
timeout /t 3

start cmd /k "streamlit run phase1_app.py"
timeout /t 3

start cmd /k "streamlit run phase2_app.py"

echo All services started.
