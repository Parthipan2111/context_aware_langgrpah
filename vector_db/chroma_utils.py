import json, uuid
from datetime import datetime

from langchain_openai import OpenAIEmbeddings
from datetime import datetime, timezone
from shared.state import GraphState
from vector_db.chroma_client import chroma_client
from dotenv import load_dotenv
from shared.session_model import SessionState


import os
load_dotenv()  # Load environment variables from .env file

history_collection = chroma_client.get_or_create_collection("conversation_history")

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small",api_key=os.getenv("OPENAI_API_KEY"))


def persist_user_messages_to_chroma(session: SessionState):
    texts, ids, metadatas = [], [], []
    if not session or not session.history:
        raise ValueError("Session or session history is empty.")

    for idx, item in enumerate(session.history):
        if item.role == "user":
            msg_id = f"{session.session_id}_{idx}"
            texts.append(clean_up_content(item.content))
            ids.append(msg_id)
            metadatas.append({
                "session_id": session.session_id,
                "user_id": session.user_id
            })

    embedding = get_embedding(texts)

    if texts:
        history_collection.upsert(
            ids=ids,
            embeddings=[embedding],  # Use the same embedding for all texts
            documents=texts,
            metadatas=metadatas
        )

def clean_up_content(content: str) -> str:
    """Clean up content by removing newlines and excessive spaces."""
    if not isinstance(content, str):
        raise ValueError("Content must be a string.")
    content = content.replace("\n", " ").replace("\r", " ")
    content = content.replace("\t", " ").replace("  ", " ")
    content = content.strip()
    return content[:1000]  # Truncate to avoid large embeddings
    
# Define embedding function
def get_embedding(text):
    if not embedding_model:
        raise ValueError("Embedder is not initialized. Check your OpenAI API key.")
    if isinstance(text, list):
        if not all(isinstance(t, str) for t in text):
            raise ValueError("All items in the list must be strings.")
        text = " ".join(text)
    return embedding_model.embed_query(text)


def query_past_history(user_id: str, query: str, n=5):
    query_embedding = get_embedding(query)
    return history_collection.query(
        query_embeddings=[query_embedding],
        n_results=n,
        where={"user_id": user_id}
    )

