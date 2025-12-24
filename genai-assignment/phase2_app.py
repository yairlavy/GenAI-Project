import streamlit as st
import requests
import base64
from pathlib import Path


# Configuration 
API_URL = "http://127.0.0.1:8000/chat"
LOGS_URL = "http://127.0.0.1:8000/logs"  # Endpoint for fetching logs

st.set_page_config(
    page_title="עוזר שירותי בריאות",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Background + Global UI Styling
def apply_background_image():
    """
    Applies background image, RTL support, and refined UI styling.
    Uses explicit path resolution to ensure image loading.
    """
    # Resolve absolute path to image
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
        /* Global RTL support */
        html, body {{
            direction: rtl;
            text-align: right;
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

        /* Make the content container semi-transparent */
        .block-container {{
            background-color: rgba(255, 255, 255, 0.95);
            padding: 3rem 3.5rem;
            border-radius: 18px;
            max-width: 900px;
            margin: 3rem auto;
            box-shadow: 0 20px 45px rgba(0,0,0,0.18);
        }}

        /* Headers */
        h1 {{
            text-align: center;
            color: #0f172a;
            margin-bottom: 0.5rem;
        }}

        hr {{
            margin: 2rem 0;
            border: none;
            height: 1px;
            background: linear-gradient(to left, #cbd5e1, transparent);
        }}

        /* Chat message container */
        section[data-testid="stChatMessage"] {{
            direction: rtl;
        }}

        /* User bubble */
        div[data-testid="stChatMessage"]:has(svg[aria-label="user"]) {{
            background-color: #e0f2fe;
            border-radius: 16px;
            padding: 1rem 1.2rem;
            margin-bottom: 0.75rem;
        }}

        /* Assistant bubble */
        div[data-testid="stChatMessage"]:has(svg[aria-label="assistant"]) {{
            background-color: #f8fafc;
            border-radius: 16px;
            padding: 1rem 1.2rem;
            margin-bottom: 0.75rem;
            border: 1px solid #e5e7eb;
        }}

        /* Chat input */
        textarea {{
            border-radius: 14px !important;
            padding: 0.75rem !important;
        }}

        /* Phase indicators */
        .phase-box {{
            padding: 0.8rem 1rem;
            border-radius: 12px;
            margin-bottom: 1.2rem;
            font-weight: 500;
        }}

        .phase-info {{
            background-color: #ecfeff;
            border: 1px solid #67e8f9;
            color: #0e7490;
        }}

        .phase-success {{
            background-color: #ecfdf5;
            border: 1px solid #6ee7b7;
            color: #065f46;
        }}
        
        /* Chat input RTL fix */
        div[data-testid="stChatInput"] textarea {{
            direction: rtl !important;
            text-align: right !important;
            unicode-bidi: plaintext;
            font-size: 1rem;
        }}

        div[data-testid="stChatInput"] textarea::placeholder {{
            direction: rtl;
            text-align: right;
            color: #6b7280;
        }}

        div[data-testid="stChatInput"] button {{
            transform: scaleX(-1);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def display_debug_logs():
    """
    Fetches and displays backend logs in the sidebar.
    This creates a 'Developer Mode' feel for the assignment.
    """
    st.sidebar.title("🛠️ Developer Logs")
    st.sidebar.caption("Live backend activity stream")
    
    try:
        # Fetch logs from our new API endpoint
        log_response = requests.get(LOGS_URL)
        
        if log_response.status_code == 200:
            logs = log_response.json().get("logs", [])
            
            if not logs:
                st.sidebar.info("No logs available yet.")
            else:
                # Combine lines and display in a code block for readability
                # We reverse them to show newest at the bottom or top as preferred
                # Here we just show them as is
                log_text = "".join(logs)
                st.sidebar.code(log_text, language="log")
        else:
            st.sidebar.error("Could not fetch logs.")
            
    except Exception:
        st.sidebar.warning("API not reachable for logs.")

apply_background_image()

# Header & Description
st.markdown("<h1>עוזר שירותי בריאות</h1>", unsafe_allow_html=True)

st.markdown(
    """
    העוזר הדיגיטלי מסייע במתן מידע על שירותי קופות החולים בישראל.  
    תחילה אשמח אם תשתפו מספר פרטים אישיים,  
    ולאחר מכן ניתן לשאול שאלות על שירותים רפואיים הזמינים עבורך.
    """
)

st.markdown("<hr>", unsafe_allow_html=True)


# Client-side State 
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}

if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "phase" not in st.session_state:
    st.session_state.phase = "collecting_info"

# Phase Indicator
if st.session_state.phase == "collecting_info":
    st.markdown(
        "<div class='phase-box phase-info'> שלב נוכחי: איסוף פרטים אישיים</div>",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<div class='phase-box phase-success'> שלב נוכחי: שאלות על שירותים רפואיים</div>",
        unsafe_allow_html=True
    )

# Display Conversation History
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat Input 
user_input = st.chat_input("")

if user_input:
    # Add user message to local state
    st.session_state.conversation.append(
        {"role": "user", "content": user_input}
    )

    #Prepare payload
    payload = {
        "message": user_input,
        "language": "he",
        "user_profile": st.session_state.user_profile,
        "conversation_history": st.session_state.conversation
    }

    #Call API
    with st.spinner("חושב..."):
        try:
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            data = response.json()

            # 4. Update state with assistant response
            st.session_state.conversation.append(
                {"role": "assistant", "content": data["reply"]}
            )

            st.session_state.user_profile = data["updated_user_profile"]
            st.session_state.phase = data["next_phase"]
            
            # Force rerender to show new message
            st.rerun()
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error communicating with server: {e}")

# Call the debug logs function at the end so it renders in the sidebar
display_debug_logs()