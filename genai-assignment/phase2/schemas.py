from pydantic import BaseModel
from typing import List, Optional, Literal


class UserProfile(BaseModel):
    """
    Holds user info.
    We use simple 'str' types instead of 'Literal' to support both 
    Hebrew and English values (e.g., "Gold" vs "זהב", "Maccabi" vs "מכבי").
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    id_number: Optional[str] = None
    gender: Optional[str] = None       # Can be "Male", "Female", "זכר", "נקבה"
    age: Optional[int] = None
    hmo: Optional[str] = None          # Can be "Maccabi", "Clalit", "מכבי", etc.
    hmo_card_number: Optional[str] = None
    insurance_tier: Optional[str] = None # Can be "Gold", "Platinum", "זהב"...


class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str


class ChatRequest(BaseModel):
    """
    Represents the request sent from Streamlit to FastAPI.
    Includes the 'language' field we added.
    """
    message: str
    conversation_history: List[ChatMessage] = []
    user_profile: UserProfile = UserProfile()
    language: str = "he"  # Default to Hebrew if missing


class ChatResponse(BaseModel):
    reply: str
    updated_user_profile: UserProfile
    next_phase: str  # "collecting_info" or "qa"