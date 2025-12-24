from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Dict

# Import the embedding function
from phase2.llm_client import get_embedding


def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """
    Splits text into smaller chunks for better semantic search.
    Simple splitting by double newlines (paragraphs) or size.
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks


def load_knowledge(base_path: Path) -> List[Dict]:
    """
    Loads HTML files, chunks them, and generates embeddings for each chunk.
    Returns a list of dicts (the "Vector Store").
    
    Structure:
    [
        {
            "text": "...",
            "embedding": [0.1, 0.2, ...],
            "source": "dental_services"
        },
        ...
    ]
    """
    vector_store = []
    
    print("Loading knowledge base and generating embeddings... (This may take a moment)")

    for html_file in base_path.glob("*.html"):
        service_name = html_file.stem

        with open(html_file, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        clean_text = soup.get_text(separator="\n")
        
        # Create chunks
        chunks = chunk_text(clean_text)
        
        for chunk in chunks:
            if not chunk.strip():
                continue
                
            # Generate embedding for this chunk
            vector = get_embedding(chunk)
            
            vector_store.append({
                "text": chunk,
                "embedding": vector,
                "source": service_name
            })
            
    print(f"Knowledge base loaded. Total chunks: {len(vector_store)}")
    return vector_store