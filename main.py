import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

import fitz
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import anthropic

app = FastAPI(title="AskMyDocs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading embedding model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded!")

sessions = {}

def extract_text_from_pdf(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i: i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def build_faiss_index(chunks):
    embeddings = embedder.encode(chunks, show_progress_bar=False)
    embeddings = np.array(embeddings).astype("float32")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index

def search_similar_chunks(query, index, chunks, top_k=5):
    query_vector = embedder.encode([query]).astype("float32")
    k = min(top_k, len(chunks))
    distances, indices = index.search(query_vector, k)
    return [chunks[i] for i in indices[0] if i < len(chunks)]

@app.get("/")
def serve_frontend():
    return FileResponse("index.html", media_type="text/html")

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        pdf_bytes = await file.read()
        text = extract_text_from_pdf(pdf_bytes)
        if len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
        chunks = chunk_text(text)
        if not chunks:
            raise HTTPException(status_code=400, detail="No content found in PDF.")
        index = build_faiss_index(chunks)
        session_id = str(uuid.uuid4())
        sessions[session_id] = {"index": index, "chunks": chunks, "filename": file.filename}
        print(f"Session created: {session_id}, chunks: {len(chunks)}")
        return {"session_id": session_id, "filename": file.filename, "chunks_count": len(chunks), "message": "Ready!"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

class QuestionRequest(BaseModel):
    session_id: str
    question: str

@app.post("/ask")
async def ask_question(req: QuestionRequest):
    try:
        if req.session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session expired. Please upload your PDF again.")

        session = sessions[req.session_id]
        relevant_chunks = search_similar_chunks(req.question, session["index"], session["chunks"])

        if not relevant_chunks:
            raise HTTPException(status_code=400, detail="No relevant content found.")

        # Check API key exists
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured. Please add ANTHROPIC_API_KEY in Space settings.")

        context = "\n\n".join(relevant_chunks)
        prompt = f"""Answer the question based on this document:

{context}

Question: {req.question}

Answer clearly and concisely."""

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        answer = message.content[0].text
        return {"answer": answer, "chunks_used": len(relevant_chunks)}

    except HTTPException:
        raise
    except anthropic.AuthenticationError:
        raise HTTPException(status_code=500, detail="Invalid API key. Please check your ANTHROPIC_API_KEY in Space settings.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/health")
def health():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    return {
        "status": "ok",
        "sessions_active": len(sessions),
        "api_key_set": bool(api_key),
        "api_key_prefix": api_key[:12] + "..." if api_key else "NOT SET"
    }
