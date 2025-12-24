from pydantic import BaseModel
from typing import List, Optional, Literal


class UserProfile(BaseModel):
    """
    Holds all user-specific information collected during the
    information collection phase.
    """

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    id_number: Optional[str] = None

    gender: Optional[Literal["male", "female"]] = None
    age: Optional[int] = None

    hmo: Optional[Literal["מכבי", "מאוחדת", "כללית"]] = None
    hmo_card_number: Optional[str] = None
    insurance_tier: Optional[Literal["זהב", "כסף", "ארד"]] = None


class ChatMessage(BaseModel):
    """
    Represents a single message in the conversation history
    with a specific role.
    """
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    """
    Represents a single chat request sent from the client to the API.
    """

    message: str
    language: Literal["he", "en"]
    user_profile: UserProfile

    # Updated to accept structured messages with roles
    conversation_history: List[ChatMessage]


class ChatResponse(BaseModel):
    """
    Represents the response returned to the client.
    """
    reply: str
    updated_user_profile: UserProfile
    next_phase: Literal["collecting_info", "qa"]