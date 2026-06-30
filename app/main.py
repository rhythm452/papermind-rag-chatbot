from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import (
    UploadResponse, AskRequest, AskResponse, SearchRequest, SearchResponse,
    ChunkResult, ParseRequest, ScorecardRequest, FitRequest, FitResponse,
    CompareRequest, CompareResponse,
)
from app.ingest import ingest_pdf, load_index
from app.retriever import search
from app.llm import generate_answer, extract_resume_info, score_resume, score_fit, compare_resumes, get_followup_questions
import fitz

app = FastAPI(title="PaperMind API", version="3.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

doc_texts: dict[str, str] = {}

@app.get("/")
def root():
    return {"message": "PaperMind API v3 running. Visit /docs"}

@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    try:
        doc_id, total_chunks, total_pages = ingest_pdf(pdf_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = "\n".join(page.get_text("text") for page in doc)
    doc_texts[doc_id] = full_text
    return UploadResponse(message="Ingested successfully.", doc_id=doc_id, total_chunks=total_chunks, total_pages=total_pages)

@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    try:
        chunks = search(request.doc_id, request.question)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Document '{request.doc_id}' not found.")
    if not chunks:
        raise HTTPException(status_code=404, detail="No relevant content found.")
    answer = generate_answer(question=request.question, chunks=chunks, chat_history=request.chat_history, mode=request.mode or "document")
    followups = get_followup_questions(request.question, answer)
    sources = [ChunkResult(text=c["text"][:300] + "..." if len(c["text"]) > 300 else c["text"], page=c["page"], score=round(c["score"], 4)) for c in chunks]
    return AskResponse(answer=answer, sources=sources, doc_id=request.doc_id, followup_questions=followups)

@app.post("/parse")
def parse_resume(request: ParseRequest):
    if request.doc_id not in doc_texts:
        raise HTTPException(status_code=404, detail=f"Document '{request.doc_id}' not found. Re-upload to use /parse.")
    result = extract_resume_info(doc_texts[request.doc_id])
    return {"doc_id": request.doc_id, "parsed": result}

@app.post("/scorecard")
def scorecard(request: ScorecardRequest):
    if request.doc_id not in doc_texts:
        raise HTTPException(status_code=404, detail=f"Document '{request.doc_id}' not found.")
    result = score_resume(doc_texts[request.doc_id])
    return {"doc_id": request.doc_id, "scorecard": result}

@app.post("/fit", response_model=FitResponse)
def score_resume_fit(request: FitRequest):
    if request.doc_id not in doc_texts:
        raise HTTPException(status_code=404, detail=f"Document '{request.doc_id}' not found.")
    analysis = score_fit(doc_texts[request.doc_id], request.job_description)
    return FitResponse(doc_id=request.doc_id, analysis=analysis)

@app.post("/compare", response_model=CompareResponse)
def compare_candidates(request: CompareRequest):
    if len(request.doc_ids) != len(request.names):
        raise HTTPException(status_code=400, detail="doc_ids and names must match.")
    resumes = []
    for doc_id, name in zip(request.doc_ids, request.names):
        if doc_id not in doc_texts:
            raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
        resumes.append({"name": name, "text": doc_texts[doc_id]})
    analysis = compare_resumes(resumes, request.role)
    return CompareResponse(role=request.role, analysis=analysis)

@app.post("/search", response_model=SearchResponse)
def semantic_search(request: SearchRequest):
    try:
        chunks = search(request.doc_id, request.query, top_k=request.top_k)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Document '{request.doc_id}' not found.")
    return SearchResponse(query=request.query, results=[ChunkResult(text=c["text"], page=c["page"], score=round(c["score"], 4)) for c in chunks])