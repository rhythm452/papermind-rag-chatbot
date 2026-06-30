import os
import json
import re
from groq import Groq
from dotenv import load_dotenv
from app.config import GROQ_MODEL

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

RESUME_SYSTEM_PROMPT = """You are an expert HR assistant and resume analyst.
You are given excerpts from a resume and must answer questions about the candidate accurately.
Rules:
1. Only use information present in the resume excerpts provided.
2. Be specific — mention exact job titles, company names, years, skills as written in the resume.
3. If something is NOT in the resume, say "This information is not mentioned in the resume."
4. Never invent or assume details not present in the text.
5. When listing skills or experience, be concise and structured."""

DOCUMENT_SYSTEM_PROMPT = """You are an expert research analyst and document assistant.
You are given excerpts from a document and must answer questions about it accurately.
Rules:
1. Only use information present in the document excerpts provided.
2. Be specific — cite figures, section names, and author claims as written in the document.
3. If something is NOT in the excerpts, say "This information is not found in the provided excerpts."
4. Never invent facts, statistics, or conclusions not present in the text.
5. For summaries, be structured and cover the key points clearly."""

EXTRACT_SYSTEM_PROMPT = """You are a resume parser. Extract structured information from the resume text provided.
Return ONLY a valid JSON object with these exact keys:
{
  "name": "full name or null",
  "email": "email or null",
  "phone": "phone or null",
  "location": "city/country or null",
  "summary": "2-3 sentence professional summary or null",
  "skills": ["skill1", "skill2"],
  "experience": [{"title": "job title", "company": "company name", "duration": "dates", "description": "brief description"}],
  "education": [{"degree": "degree name", "institution": "school name", "year": "graduation year or null"}],
  "projects": [{"name": "project name", "description": "brief description", "technologies": ["tech1"]}],
  "certifications": ["cert1"]
}
Return only the JSON. No explanation, no markdown, no backticks."""

SCORECARD_SYSTEM_PROMPT = """You are an expert resume evaluator. Score this resume on these 5 categories out of 10 each.
Return ONLY a valid JSON object:
{
  "skills": {"score": 8, "comment": "Strong Python and ML skills"},
  "experience": {"score": 7, "comment": "2 years relevant experience"},
  "education": {"score": 9, "comment": "Top university degree"},
  "projects": {"score": 8, "comment": "3 impressive projects with real impact"},
  "overall": {"score": 8, "comment": "Strong candidate overall"}
}
Be honest and specific. No explanation outside the JSON."""

FIT_SYSTEM_PROMPT = """You are a technical recruiter evaluating candidate-job fit.
Given a resume and a job description, provide:
1. A fit score from 0-100
2. Top 3 matching strengths
3. Top 3 gaps or missing requirements
4. A one-paragraph hiring recommendation
Be specific and reference actual details from the resume."""

COMPARE_SYSTEM_PROMPT = """You are a senior technical recruiter comparing multiple candidates.
Given resumes and a job description (or role), rank the candidates and explain your reasoning.
Be specific — reference actual skills, experience, and projects from each resume."""

FOLLOWUP_SYSTEM_PROMPT = """You are a helpful assistant. Based on the question asked and the answer given about a document,
suggest exactly 3 short follow-up questions the user might want to ask next.
Return ONLY a JSON array of 3 strings. Example: ["What technologies did they use?", "How many years of experience?", "What was their role?"]
No explanation, no markdown, just the JSON array."""


def build_prompt(question: str, chunks: list[dict]) -> str:
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(f"[Excerpt {i} — Page {chunk['page']}]\n{chunk['text']}")
    context = "\n\n---\n\n".join(context_parts)
    return f"""Document excerpts:\n\n{context}\n\n---\n\nQuestion: {question}"""


def generate_answer(question: str, chunks: list[dict], chat_history: list[dict] | None = None, mode: str = "document") -> str:
    system_prompt = RESUME_SYSTEM_PROMPT if mode == "resume" else DOCUMENT_SYSTEM_PROMPT
    messages = [{"role": "system", "content": system_prompt}]
    if chat_history:
        for turn in chat_history[-6:]:
            messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": build_prompt(question, chunks)})
    response = client.chat.completions.create(model=GROQ_MODEL, messages=messages, temperature=0.2, max_tokens=1024)
    return response.choices[0].message.content.strip()


def get_followup_questions(question: str, answer: str) -> list[str]:
    messages = [
        {"role": "system", "content": FOLLOWUP_SYSTEM_PROMPT},
        {"role": "user", "content": f"Question asked: {question}\n\nAnswer given: {answer[:500]}\n\nSuggest 3 follow-up questions."}
    ]
    response = client.chat.completions.create(model=GROQ_MODEL, messages=messages, temperature=0.4, max_tokens=200)
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        questions = json.loads(raw)
        return questions[:3] if isinstance(questions, list) else []
    except Exception:
        return []


def extract_resume_info(full_text: str) -> dict:
    messages = [
        {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
        {"role": "user", "content": f"Parse this resume:\n\n{full_text[:6000]}"},
    ]
    response = client.chat.completions.create(model=GROQ_MODEL, messages=messages, temperature=0.0, max_tokens=2048)
    raw = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except Exception:
        return {"error": "Could not parse resume structure", "raw": raw}


def score_resume(full_text: str) -> dict:
    messages = [
        {"role": "system", "content": SCORECARD_SYSTEM_PROMPT},
        {"role": "user", "content": f"Score this resume:\n\n{full_text[:5000]}"},
    ]
    response = client.chat.completions.create(model=GROQ_MODEL, messages=messages, temperature=0.1, max_tokens=512)
    raw = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except Exception:
        return {"error": "Could not score resume"}


def score_fit(resume_text: str, job_description: str) -> str:
    messages = [
        {"role": "system", "content": FIT_SYSTEM_PROMPT},
        {"role": "user", "content": f"RESUME:\n{resume_text[:4000]}\n\nJOB DESCRIPTION:\n{job_description}"},
    ]
    response = client.chat.completions.create(model=GROQ_MODEL, messages=messages, temperature=0.3, max_tokens=1024)
    return response.choices[0].message.content.strip()


def compare_resumes(resumes: list[dict], role: str) -> str:
    resume_blocks = [f"--- CANDIDATE {i+1}: {r['name']} ---\n{r['text'][:2500]}" for i, r in enumerate(resumes)]
    combined = "\n\n".join(resume_blocks)
    messages = [
        {"role": "system", "content": COMPARE_SYSTEM_PROMPT},
        {"role": "user", "content": f"Role: {role}\n\n{combined}\n\nRank and compare these candidates."},
    ]
    response = client.chat.completions.create(model=GROQ_MODEL, messages=messages, temperature=0.3, max_tokens=1500)
    return response.choices[0].message.content.strip()