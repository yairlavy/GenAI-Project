from fastapi import FastAPI, Request
from pathlib import Path
import math
import time

from phase2.schemas import ChatRequest, ChatResponse
from phase2.prompts import (
    user_information_collection_prompt,
    qa_prompt
)
from phase2.knowledge_loader import load_knowledge
from phase2.llm_client import call_llm, get_embedding
from phase2.extraction import extract_user_info
from phase2.logger import logger  # Import our new logger


app = FastAPI(
    title="Medical Services Chatbot API",
    description="Stateless chatbot microservice for Israeli health funds",
    version="1.0"
)

# Load knowledge base (Vector Store) at startup
logger.info("Starting up API...")
BASE_DIR = Path(__file__).parent
try:
    VECTOR_STORE = load_knowledge(BASE_DIR / ".." / "phase2_data")
    logger.info(f"Successfully loaded {len(VECTOR_STORE)} knowledge chunks.")
except Exception as e:
    logger.critical(f"Failed to load knowledge base: {e}")
    VECTOR_STORE = []


def is_profile_complete(profile) -> bool:
    return all([
        profile.first_name,
        profile.last_name,
        profile.id_number,
        profile.gender,
        profile.age,
        profile.hmo,
        profile.hmo_card_number,
        profile.insurance_tier
    ])


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude1 = math.sqrt(sum(a * a for a in v1))
    magnitude2 = math.sqrt(sum(b * b for b in v2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
        
    return dot_product / (magnitude1 * magnitude2)


def search_knowledge(query: str, top_k: int = 3) -> str:
    #Embed the user query
    query_vector = get_embedding(query)
    
    #Calculate similarity with all chunks
    scored_chunks = []
    for item in VECTOR_STORE:
        score = cosine_similarity(query_vector, item["embedding"])
        scored_chunks.append((score, item["text"]))
    
    #Sort by score (descending)
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    #Take top K chunks
    top_chunks = [chunk for score, chunk in scored_chunks[:top_k]]
    
    logger.info(f"Knowledge Search: Found {len(top_chunks)} chunks for query: '{query}'")
    return "\n\n---\n\n".join(top_chunks)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    start_time = time.time()
    user_profile = request.user_profile
    
    logger.info(f"Incoming request | User ID: {user_profile.id_number or 'Unknown'} | Phase: { 'QA' if is_profile_complete(user_profile) else 'Collection' }")

    try:
        # --- Phase 1: Collect User Info ---
        if not is_profile_complete(user_profile):
            system_prompt = user_information_collection_prompt(request.language)

            messages = [{"role": "system", "content": system_prompt}]
            messages.extend([msg.model_dump() for msg in request.conversation_history])
            messages.append({"role": "user", "content": request.message})

            assistant_reply = call_llm(messages)
            
            extracted_fields = extract_user_info(
                message=request.message,
                language=request.language
            )
            
            if extracted_fields:
                logger.info(f"Extracted fields: {list(extracted_fields.keys())}")
            
            for field, value in extracted_fields.items():
                if getattr(user_profile, field) is None and value is not None:
                    setattr(user_profile, field, value)

            next_phase = "qa" if is_profile_complete(user_profile) else "collecting_info"
            
            if next_phase == "qa":
                logger.info("User profile completed. Transitioning to QA phase.")
            
            return ChatResponse(
                reply=assistant_reply,
                updated_user_profile=user_profile,
                next_phase=next_phase
            )

        # --- Phase 2: Q&A with RAG ---
        
        # Search for relevant information based on user message
        relevant_context = search_knowledge(request.message)

        if not relevant_context:
            logger.warning("No relevant context found in Vector Store.")
            relevant_context = "No specific information found in the knowledge base."

        # Inject context + User HMO info into prompt using XML tags for security
        hmo_info = (
            f"<user_context>"
            f"<hmo>{user_profile.hmo}</hmo>"
            f"<tier>{user_profile.insurance_tier}</tier>"
            f"</user_context>"
        )
        
        combined_context = (
            f"{hmo_info}\n\n"
            f"<retrieved_knowledge>\n{relevant_context}\n</retrieved_knowledge>"
        )

        system_prompt = qa_prompt(request.language, combined_context)

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend([msg.model_dump() for msg in request.conversation_history])
        messages.append({"role": "user", "content": request.message})

        assistant_reply = call_llm(messages)

        logger.info(f"Request processed successfully in {time.time() - start_time:.2f}s")
        
        return ChatResponse(
            reply=assistant_reply,
            updated_user_profile=user_profile,
            next_phase="qa"
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        # Return a polite error message to the user instead of crashing
        return ChatResponse(
            reply="אירעה שגיאה במערכת. אנא נסה שנית מאוחר יותר.\nAn error occurred. Please try again later.",
            updated_user_profile=user_profile,
            next_phase="collecting_info" if not is_profile_complete(user_profile) else "qa"
        )

@app.get("/logs")
def get_logs():
    """
    Returns the last 50 lines of the log file.
    Useful for demonstrating backend logic in the UI.
    """
    log_file_path = Path(__file__).parent / ".." / "logs" / "chatbot.log"
    
    if not log_file_path.exists():
        return {"logs": ["Log file not created yet."]}
        
    try:
        with open(log_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Return last 50 lines to avoid payload being too large
            return {"logs": lines[-50:]}
    except Exception as e:
        return {"logs": [f"Error reading logs: {str(e)}"]}