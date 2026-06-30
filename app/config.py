from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-8b-8192")

TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", 20))
TOP_K_RERANK: int = int(os.getenv("TOP_K_RERANK", 5))
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 50))

VECTOR_STORE_DIR: str = "vector_store"
EMBED_MODEL: str = "all-MiniLM-L6-v2"
RERANK_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
