---
title: PaperMind
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
app_port: 7860
---

# PaperMind — Resume & Document Intelligence

RAG-powered chatbot that lets you chat with resumes and documents using FastAPI, FAISS, sentence-transformers, and LLaMA 3 via Groq.

## Features
- Chat with any PDF (resume or document)
- Resume parsing into structured JSON
- AI score card with category ratings
- Experience timeline visualization
- Job fit scoring
- Multi-candidate comparison
- Multi-language support (English, Hindi, Spanish, French, German)
- Voice input

## Setup
You need to add your `GROQ_API_KEY` as a secret in this Space's settings (Settings → Repository secrets).
Get a free key at https://console.groq.com