from pydantic import BaseModel
from typing import Optional

class UploadResponse(BaseModel):
    message: str
    doc_id: str
    total_chunks: int
    total_pages: int

class AskRequest(BaseModel):
    doc_id: str
    question: str
    chat_history: Optional[list[dict]] = []
    mode: Optional[str] = "document"

class ChunkResult(BaseModel):
    text: str
    page: int
    score: float

class AskResponse(BaseModel):
    answer: str
    sources: list[ChunkResult]
    doc_id: str
    followup_questions: Optional[list[str]] = []

class SearchRequest(BaseModel):
    doc_id: str
    query: str
    top_k: Optional[int] = 5

class SearchResponse(BaseModel):
    query: str
    results: list[ChunkResult]

class ParseRequest(BaseModel):
    doc_id: str

class ScorecardRequest(BaseModel):
    doc_id: str

class FitRequest(BaseModel):
    doc_id: str
    job_description: str

class FitResponse(BaseModel):
    doc_id: str
    analysis: str

class CompareRequest(BaseModel):
    doc_ids: list[str]
    names: list[str]
    role: str

class CompareResponse(BaseModel):
    role: str
    analysis: str