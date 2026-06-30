# RAG PDF Chatbot

A production-style document Q&A system built with:
**RAG · NLP · Semantic Search · Cross-encoder Re-ranking · LLM · FastAPI · Streamlit**

---

## How it works

```
PDF Upload → Text Extraction (PyMuPDF) → Chunking (tiktoken)
          → Embeddings (sentence-transformers) → FAISS Index

User Question → Embed Query → FAISS Retrieval (top-20)
             → Cross-encoder Re-rank (top-5) → LLM (Groq/LLaMA 3)
             → Answer + Source Citations
```

---

## Setup

### 1. Clone and install

```bash
git clone <your-repo-url>
cd rag-pdf-chatbot
pip install -r requirements.txt
```

### 2. Get a free Groq API key

Sign up at https://console.groq.com — free tier gives you fast LLaMA 3 inference.

### 3. Set your environment variables

```bash
cp .env.example .env
# Edit .env and paste your GROQ_API_KEY
```

---

## Running

### Start the FastAPI backend

```bash
uvicorn app.main:app --reload
```

API docs available at: http://localhost:8000/docs

### Start the Streamlit frontend (separate terminal)

```bash
streamlit run frontend.py
```

UI available at: http://localhost:8501

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload a PDF, returns `doc_id` |
| POST | `/ask` | Ask a question, get answer + sources |
| POST | `/search` | Semantic search, returns raw chunks (no LLM) |

### Example: Upload a PDF

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@your_document.pdf"
```

Response:
```json
{
  "message": "PDF ingested successfully.",
  "doc_id": "a1b2c3d4",
  "total_chunks": 142,
  "total_pages": 18
}
```

### Example: Ask a question

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "doc_id": "a1b2c3d4",
    "question": "What are the main findings?",
    "chat_history": []
  }'
```

### Example: Semantic search (no LLM)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "doc_id": "a1b2c3d4",
    "query": "risk factors",
    "top_k": 3
  }'
```

---

## Project structure

```
rag-pdf-chatbot/
├── app/
│   ├── __init__.py
│   ├── config.py      # environment variables and settings
│   ├── models.py      # Pydantic request/response schemas
│   ├── ingest.py      # PDF → chunks → embeddings → FAISS
│   ├── retriever.py   # semantic search + cross-encoder re-ranking
│   ├── llm.py         # prompt builder + Groq LLM call
│   └── main.py        # FastAPI endpoints
├── vector_store/       # saved FAISS indexes (auto-created)
├── frontend.py         # Streamlit UI
├── requirements.txt
├── .env.example
└── README.md
```

---

## Key concepts (for interviews)

**Why RAG over fine-tuning?**
RAG is cheaper, faster to update, and cites sources. Fine-tuning bakes knowledge into weights — expensive and can't be easily updated when the document changes.

**Why two-stage retrieval?**
Bi-encoders (FAISS) are fast but approximate. Cross-encoders are slow but accurate. We run FAISS on thousands of chunks to get 20 candidates, then the cross-encoder precisely scores just those 20.

**Why chunk overlap?**
If a key sentence falls at the boundary between two chunks, half goes to each — neither chunk has the full context. Overlap ensures boundary content always appears complete in at least one chunk.

**Why low temperature (0.2)?**
We want factual, grounded answers — not creative ones. Low temperature makes the LLM stick closely to the provided context.
