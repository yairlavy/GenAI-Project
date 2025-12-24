import os
from dotenv import load_dotenv
from openai import AzureOpenAI


# Load environment variables from .env file.
load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")

if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_KEY:
    raise RuntimeError("Missing Azure OpenAI credentials in environment variables")


client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version="2024-02-15-preview"
)


def call_llm(messages: list[dict], temperature: float = 0.0) -> str:
    """
    Sends a list of structured messages to Azure OpenAI.
    
    Expected format for 'messages':
    [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ]
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=temperature
    )

    return response.choices[0].message.content


def get_embedding(text: str) -> list[float]:
    """
    Generates a vector embedding for the given text using ADA-002.
    Used for semantic search in the knowledge base.
    """
    # Ensure text is not empty or too long
    text = text.replace("\n", " ")
    
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-ada-002"
    )
    
    return response.data[0].embedding