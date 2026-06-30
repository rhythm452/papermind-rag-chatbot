FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Create vector_store directory
RUN mkdir -p vector_store

# Hugging Face Spaces expects the app on port 7860
EXPOSE 7860

# Run both FastAPI (internal, port 8000) and Streamlit (public, port 7860)
CMD bash -c "uvicorn app.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend.py --server.port 7860 --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false"