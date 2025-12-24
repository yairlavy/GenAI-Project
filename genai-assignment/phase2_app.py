import streamlit as st
import requests
import base64
from pathlib import Path


# Configuration 
API_URL = "http://127.0.0.1:8000/chat"
LOGS_URL = "http://127.0.0.1:8000/logs"

st.set_page_config(
    page_title="Health Services Assistant",
    layout="centered",
    initial_sidebar_state="expanded"
)


#UI & Styling Helper Functions 

def apply_base_styling():
    """
    Applies the background image and basic container styling.
    """
    current_dir = Path(__file__).parent.resolve()
    background_path = current_dir / "UI" / "background.png"
    
    encoded_image = ""
    if background_path.exists():
        encoded_image = base64.b64encode(background_path.read_bytes()).decode()
    
    st.markdown(
        f"""
        <style>
        /* Base Font */
        html, body {{
            font-family: "Segoe UI", sans-serif;
        }}
        
        /* Background Image */
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_image}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}

        /* White semi-transparent container */
        .block-container {{
            background-color: rgba(255, 255, 255, 0.95);
            padding: 3rem 3.5rem;
            border-radius: 18px;
            max-width: 900px;
            margin: 3rem auto;
            box-shadow: 0 20px 45px rgba(0,0,0,0.18);
        }}

        /* Chat bubbles styling */
        div[data-testid="stChatMessage"] {{
            border-radius: 16px;
            padding: 1rem;
            margin-bottom: 0.5rem;
        }}

        /* Chat input font size */
        div[data-testid="stChatInput"] textarea {{
            font-size: 1rem;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def apply_dynamic_styling(direction):
    """
    Applies RTL or LTR styling based on selected language.
    """
    align = "right" if direction == "rtl" else "left"
    
    st.markdown(
        f"""
        <style>
        /* Adjust direction for main container, inputs, and markdown */
        .block-container, input, textarea, .stMarkdown, p, h1, h2, h3 {{
            direction: {direction};
            text-align: {align};
        }}
        
        /* Fix Chat Input Button position based on direction */
        div[data-testid="stChatInput"] button {{
            transform: {'scaleX(-1)' if direction == 'rtl' else 'none'};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def display_sidebar():
    """
    Renders the Language Selector and Developer Logs in the sidebar.
    Returns the selected language code ('he' or 'en').
    """
    st.sidebar.title("Settings / הגדרות")
    
    # Language Selector 
    lang_choice = st.sidebar.radio(
        "Language / שפה:",
        options=["עברית HE", "English EN"],
        index=0
    )
    
    lang_code = "he" if "עברית" in lang_choice else "en"
    
    st.sidebar.markdown("---")
    
    # Developer Logs 
    st.sidebar.title("Developer Logs")
    st.sidebar.caption("Live backend activity stream")
    
    # Retrieve access token from Streamlit URL query params
    # Usage: http://localhost:8501/?access=admin
    query_params = st.query_params
    access_token = query_params.get("access", None)
    
    try:
        # Pass the access token to the backend API
        params = {"access": access_token} if access_token else {}
        log_response = requests.get(LOGS_URL, params=params)
        
        if log_response.status_code == 200:
            logs = log_response.json().get("logs", [])
            if logs:
                log_text = "".join(logs)
                st.sidebar.code(log_text, language="log")
            else:
                st.sidebar.info("No logs yet.")
        else:
            st.sidebar.error("Could not fetch logs.")
    except Exception:
        st.sidebar.warning("API not reachable.")

    return lang_code


#  Text Content Dictionary 

TEXTS = {
    "he": {
        "title": "עוזר שירותי בריאות",
        "intro": """
        העוזר הדיגיטלי מסייע במתן מידע על שירותי קופות החולים בישראל.  
        תחילה אשמח אם תשתפו מספר פרטים אישיים, ולאחר מכן ניתן לשאול שאלות על שירותים רפואיים.
        """,
        "phase_info": "שלב נוכחי: איסוף פרטים אישיים",
        "phase_qa": "שלב נוכחי: שאלות על שירותים רפואיים",
        "placeholder": "הקלד הודעה כאן...",
        "spinner": "חושב...",
        "dir": "rtl"
    },
    "en": {
        "title": "Health Services Assistant",
        "intro": """
        The digital assistant provides information on Israeli Health Fund services.
        First, please share some personal details, and then you can ask questions about available medical services.
        """,
        "phase_info": "Current Phase: Collecting Personal Info",
        "phase_qa": "Current Phase: Medical Services Q&A",
        "placeholder": "Type your message here...",
        "spinner": "Thinking...",
        "dir": "ltr"
    }
}


# Main Application Flow 

# Apply base background
apply_base_styling()

# Get Language Selection
selected_lang = display_sidebar()
t = TEXTS[selected_lang] # Get text dictionary for selected language

# Apply Direction (RTL/LTR)
apply_dynamic_styling(t["dir"])

#  Header & Intro 
st.markdown(f"<h1>{t['title']}</h1>", unsafe_allow_html=True)
st.markdown(t['intro'])
st.markdown("<hr>", unsafe_allow_html=True)


#  Session State Initialization 
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}

if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "phase" not in st.session_state:
    st.session_state.phase = "collecting_info"


#  Phase Indicator 
if st.session_state.phase == "collecting_info":
    st.info(t["phase_info"])
else:
    st.success(t["phase_qa"])


#  Display Chat History 
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.write(message["content"])


#  Chat Input & Logic 
user_input = st.chat_input(t["placeholder"])

if user_input:
    # Add user message to history
    st.session_state.conversation.append(
        {"role": "user", "content": user_input}
    )

    # Prepare Payload 
    payload = {
        "message": user_input,
        "language": selected_lang,  # Sends 'he' or 'en'
        "user_profile": st.session_state.user_profile,
        "conversation_history": st.session_state.conversation
    }

    #Call API
    with st.spinner(t["spinner"]):
        try:
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            data = response.json()

            # 4. Update UI with Assistant Response
            st.session_state.conversation.append(
                {"role": "assistant", "content": data["reply"]}
            )

            st.session_state.user_profile = data["updated_user_profile"]
            st.session_state.phase = data["next_phase"]
            
            # Refresh to show new message
            st.rerun()
            
        except requests.exceptions.RequestException as e:
            st.error(f"Server Connection Error: {e}")