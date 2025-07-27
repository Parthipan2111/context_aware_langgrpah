from redis import Redis
from chromadb import Client as ChromaClient
from pymongo import MongoClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")


mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client["chat_db"]
mongo_sessions = mongo_db["sessions"]