import chromadb
from chromadb.config import Settings
import os

path = os.getcwd()
data_path = os.path.join(path, "data")
chroma_client = chromadb.PersistentClient(path=data_path)
