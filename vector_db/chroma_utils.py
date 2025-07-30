import json, uuid
from datetime import datetime

from langchain_openai import OpenAIEmbeddings
from datetime import datetime, timezone
from shared.state import GraphState
from vector_db.chroma_client import chroma_client
from dotenv import load_dotenv
from shared.session_model import SessionState
from openai import OpenAI



import os
load_dotenv()  # Load environment variables from .env file

history_collection = chroma_client.get_or_create_collection("conversation_history")

client = OpenAI()

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
    if texts:
        embeddings = get_embeddings_for_texts(texts)

        history_collection.upsert(
            ids=ids,
            embeddings=embeddings,  # Use the same embedding for all texts
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
    
# Define embedding function:
def get_embedding(text: str):
    response = embedding_model.embed_query(text)
    return response

def get_embeddings_for_texts(texts: list[str]) -> list[list[float]]:
    """
    Compute embeddings for a list of texts using a non-batch embedding API.
    Returns: list of embedding vectors
    """
    all_embeddings = []
    for t in texts:
        emb = get_embedding(t)  # returns List[float]
        all_embeddings.append(emb)
    return all_embeddings

def query_past_history(user_id: str, query: str, n=5):
    query_embedding = get_embedding(query)
    return history_collection.query(
        query_embeddings=[query_embedding],
        n_results=n,
        where={"user_id": user_id}
    )

