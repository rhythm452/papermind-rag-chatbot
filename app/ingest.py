import fitz  # PyMuPDF
import tiktoken
import numpy as np
import faiss
import pickle
import os
import uuid
from sentence_transformers import SentenceTransformer
from app.config import (
    CHUNK_SIZE, CHUNK_OVERLAP, VECTOR_STORE_DIR, EMBED_MODEL
)

# Load embedding model once at module level (cached after first load)
embedder = SentenceTransformer(EMBED_MODEL)
tokenizer = tiktoken.get_encoding("cl100k_base")


def extract_text_from_pdf(pdf_bytes: bytes) -> list[dict]:
    """
    Extract text from PDF bytes page by page.
    Returns: [{"page": int, "text": str}, ...]
    """
    pages = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").strip()
        if text:
            pages.append({"page": page_num + 1, "text": text})
    doc.close()
    return pages


def chunk_pages(pages: list[dict]) -> list[dict]:
    """
    Split pages into overlapping token-based chunks.
    Returns: [{"text": str, "page": int, "chunk_id": int}, ...]
    """
    chunks = []
    chunk_id = 0

    for page_data in pages:
        page_num = page_data["page"]
        text = page_data["text"]

        tokens = tokenizer.encode(text)

        start = 0
        while start < len(tokens):
            end = start + CHUNK_SIZE
            chunk_tokens = tokens[start:end]
            chunk_text = tokenizer.decode(chunk_tokens)

            chunks.append({
                "chunk_id": chunk_id,
                "page": page_num,
                "text": chunk_text.strip(),
            })
            chunk_id += 1

            # Move forward by CHUNK_SIZE - CHUNK_OVERLAP for overlap
            start += CHUNK_SIZE - CHUNK_OVERLAP
            if start >= len(tokens):
                break

    return chunks


def embed_chunks(chunks: list[dict]) -> np.ndarray:
    """
    Embed all chunks using sentence-transformers.
    Returns: numpy array of shape (n_chunks, embedding_dim)
    """
    texts = [c["text"] for c in chunks]
    embeddings = embedder.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    return embeddings.astype("float32")


def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """
    Build a FAISS inner-product index (equivalent to cosine sim on normalised vectors).
    """
    # Normalise embeddings so inner product == cosine similarity
    faiss.normalize_L2(embeddings)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index


def save_index(doc_id: str, index: faiss.IndexFlatIP, chunks: list[dict]) -> None:
    """
    Persist FAISS index and chunk metadata to disk.
    """
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    faiss.write_index(index, os.path.join(VECTOR_STORE_DIR, f"{doc_id}.faiss"))
    with open(os.path.join(VECTOR_STORE_DIR, f"{doc_id}.pkl"), "wb") as f:
        pickle.dump(chunks, f)


def load_index(doc_id: str) -> tuple[faiss.IndexFlatIP, list[dict]]:
    """
    Load FAISS index and chunk metadata from disk.
    Raises FileNotFoundError if doc_id doesn't exist.
    """
    index_path = os.path.join(VECTOR_STORE_DIR, f"{doc_id}.faiss")
    meta_path = os.path.join(VECTOR_STORE_DIR, f"{doc_id}.pkl")

    if not os.path.exists(index_path):
        raise FileNotFoundError(f"No index found for doc_id: {doc_id}")

    index = faiss.read_index(index_path)
    with open(meta_path, "rb") as f:
        chunks = pickle.load(f)
    return index, chunks


def ingest_pdf(pdf_bytes: bytes) -> tuple[str, int, int]:
    """
    Full ingestion pipeline: PDF → chunks → embeddings → FAISS index on disk.
    Returns: (doc_id, total_chunks, total_pages)
    """
    doc_id = str(uuid.uuid4())[:8]  # short unique ID

    pages = extract_text_from_pdf(pdf_bytes)
    if not pages:
        raise ValueError("Could not extract any text from the PDF.")

    chunks = chunk_pages(pages)
    embeddings = embed_chunks(chunks)
    index = build_faiss_index(embeddings)
    save_index(doc_id, index, chunks)

    return doc_id, len(chunks), len(pages)
