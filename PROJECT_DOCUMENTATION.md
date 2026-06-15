# AskMyDocs — Complete Project Documentation

**Built by:** Prashanth Duddukuri  
**Date:** May 2026

---

## 1. What Is This Project?

AskMyDocs is a web application that lets you upload any PDF document and ask questions about it in plain English. The AI reads your document and answers based only on what's in it — no guessing, no making things up.

**Example:**
- Upload a 100-page contract → Ask "What are the payment terms?" → Get the exact answer
- Upload a research paper → Ask "What methodology was used?" → Get a clear answer
- Upload a resume → Ask "What are the skills?" → Get a list

---

## 2. The Problem It Solves

Normal AI chatbots only know what they were trained on. They don't know YOUR documents.

AskMyDocs solves this by letting you give the AI your own document and ask questions about it — accurately, without the AI making things up (hallucination).

---

## 3. How It Works — Step by Step

```
STEP 1: User uploads a PDF
           ↓
STEP 2: Extract all text from the PDF
           ↓
STEP 3: Split text into small chunks (500 words each)
           ↓
STEP 4: Convert each chunk into numbers (embeddings/vectors)
           ↓
STEP 5: Store those numbers in a FAISS vector database
           ↓
STEP 6: User asks a question
           ↓
STEP 7: Convert question into numbers too
           ↓
STEP 8: Find the 5 most similar chunks using FAISS search
           ↓
STEP 9: Send those 5 chunks + question to Claude AI
           ↓
STEP 10: Claude reads the chunks and answers the question
           ↓
STEP 11: Answer shown to the user
```

This process is called **RAG — Retrieval Augmented Generation**.

---

## 4. Why RAG Instead of Just Sending the PDF to Claude?

This is the most important concept to understand.

**Without RAG:**
Every time someone asks a question, you send the ENTIRE document to Claude.
- A 500-page PDF = 250,000 words sent every single question
- Costs a lot of money per question
- Slow — more text = slower response
- Has a size limit — very large documents won't even fit

**With RAG:**
You only send the 5 most relevant pieces of the document.
- 5 chunks = about 2,500 words sent per question
- 100x cheaper
- Much faster
- No size limit — works for documents of any size

**Real world analogy:**
Imagine a 1000-page book. Instead of reading the whole book every time, RAG creates a smart index (like the index at the back of a book). When you ask a question, it finds the right pages instantly and only reads those.

---

## 5. Technologies Used and Why

### Python
**What:** The programming language used for the entire backend.
**Why:** Python is the #1 language for AI/ML. All the best AI libraries are in Python. Every AI company uses Python.

---

### FastAPI
**What:** A web framework that creates the API endpoints (/upload and /ask).
**Why:** FastAPI is fast, modern, and perfect for AI applications. It handles file uploads easily and is used widely in production AI systems.

**Endpoints we created:**
- `GET /` → Serves the frontend HTML page
- `POST /upload` → Receives PDF, processes it, returns session_id
- `POST /ask` → Receives question + session_id, returns answer
- `GET /health` → Shows if the server is running

---

### PyMuPDF (fitz)
**What:** A Python library that reads PDF files and extracts text.
**Why:** PDFs are binary files — you can't just read them like a text file. PyMuPDF handles all PDF formats reliably and extracts clean text from every page.

**Code:**
```python
import fitz
doc = fitz.open(stream=pdf_bytes, filetype="pdf")
for page in doc:
    text += page.get_text()
```

---

### Text Chunking
**What:** Splitting the extracted text into smaller pieces (chunks).
**Why:** You can't send a whole document to an AI at once — it has limits. Also, smaller chunks = more precise search results.

**How we did it:**
- chunk_size = 500 words per chunk
- overlap = 50 words shared between chunks

**Why overlap?**
Overlap prevents losing context at the boundaries. If a sentence starts at the end of chunk 1 and finishes at the start of chunk 2, overlap ensures both chunks have that sentence.

---

### Sentence Transformers (all-MiniLM-L6-v2)
**What:** A machine learning model that converts text into numbers (vectors/embeddings).
**Why:** Computers can't understand words directly. By converting text to numbers (vectors), we can mathematically compare meaning. Two sentences that mean the same thing will have similar numbers, even if they use different words.

**Example:**
- "How much does it cost?" → [0.2, 0.8, 0.1, 0.5, ...] (384 numbers)
- "What is the price?" → [0.21, 0.79, 0.11, 0.51, ...] (similar numbers!)

**Why this model specifically?**
- Free — runs locally, no API cost
- Small — only 80MB download
- Fast — works well on CPU
- Good quality — produces accurate embeddings

---

### FAISS (Facebook AI Similarity Search)
**What:** A database that stores vectors and finds the most similar ones extremely fast.
**Why:** When a user asks a question, we need to find which chunks are most relevant. FAISS does this search in milliseconds even with millions of chunks.

**How it works:**
1. Store all chunk vectors in FAISS index
2. Convert question to a vector
3. Ask FAISS: "which stored vectors are closest to this?"
4. FAISS returns the top 5 most similar chunks

**Why FAISS and not something else?**
- Free and open source (made by Facebook/Meta)
- Extremely fast
- Works in memory — no external database needed
- Perfect for demos and small-to-medium projects

---

### Anthropic Claude API
**What:** The AI that actually reads the relevant chunks and answers the question.
**Why Claude:** Claude is excellent at following instructions, stays truthful, and admits when it doesn't know something — perfect for document Q&A.

**How we use it:**
```
We send:  "Here are 5 relevant pieces of the document. 
           Answer this question based ONLY on these pieces: [question]"

Claude returns: A clear, accurate answer
```

**Why API key?**
Claude is a paid service. The API key:
1. Identifies who is making the request
2. Tracks usage for billing
3. Keeps the service secure

Never share your API key — it's like a password for a service you pay for.

---

### NumPy
**What:** A Python library for mathematical operations on arrays.
**Why:** FAISS needs vectors in a specific format (float32 arrays). NumPy converts the embeddings into this format.

---

### Docker
**What:** A tool that packages your entire application into a container.
**Why:** A container includes Python, all libraries, and your code. It runs exactly the same way on any computer or server — no "it works on my machine" problems.

**Our Dockerfile:**
```
FROM python:3.11-slim    ← Start with Python
COPY requirements.txt    ← Copy dependencies list
RUN pip install -r ...   ← Install all packages
COPY main.py             ← Copy our code
COPY index.html          ← Copy our frontend
EXPOSE 7860              ← Open port 7860
CMD uvicorn main:app     ← Start the server
```

---

### Hugging Face Spaces
**What:** A free hosting platform for AI applications.
**Why:** 
- Free forever for public spaces
- Recognizes Docker automatically
- Used by the entire AI community
- Hiring managers know and respect it
- Gives you a permanent public URL

---

### HTML / CSS / JavaScript (Frontend)
**What:** The user interface — what users see and interact with.
**Why vanilla HTML/JS (no React or frameworks)?**
- No build step needed
- Works immediately in any browser
- Easy to deploy — just one file
- Faster to load

---

## 6. Project File Structure

```
askmydocs/
│
├── main.py          ← Backend: all the RAG logic, API endpoints
├── index.html       ← Frontend: the UI users see
├── requirements.txt ← List of Python packages to install
├── Dockerfile       ← Instructions to build the container
└── README.md        ← Project description for GitHub
```

---

## 7. How the Files Talk to Each Other

```
User opens browser
       ↓
index.html loads (the UI)
       ↓
User uploads PDF → JavaScript sends it to POST /upload
       ↓
main.py receives PDF → extracts text → chunks → embeddings → FAISS index
main.py returns session_id to frontend
       ↓
User types question → JavaScript sends it to POST /ask
       ↓
main.py receives question → searches FAISS → calls Claude API
main.py returns answer to frontend
       ↓
JavaScript displays answer in the chat
```

---

## 8. What is a Session ID?

When you upload a PDF, the server creates a unique ID for your session — like a ticket number.

Example: `a3f7c2d1-8b4e-4f6a-9c2d-1e5f8a3b7c90`

This ID is saved in the browser. Every time you ask a question, the browser sends this ID along with the question. The server uses this ID to find YOUR FAISS index (not someone else's).

This is how the server knows which document you uploaded, even when multiple people are using the app at the same time.

---

## 9. Environment Variables / Secrets

**What is an environment variable?**
A value that is stored outside your code, in the server's environment.

**Why do we use it for the API key?**
- If we put the API key directly in main.py and pushed to GitHub, everyone could see it and use your account
- Environment variables are stored securely and never appear in your code
- On Hugging Face, you set them in Settings → Variables and Secrets

**In code:**
```python
api_key = os.environ.get("ANTHROPIC_API_KEY")
```
This reads the secret value from the environment at runtime.

---

## 10. What You Can Say in an Interview

**Q: Tell me about a project you built.**

**A:** "I built AskMyDocs — a RAG-powered PDF chat application. Users upload any PDF and ask questions about it in natural language. 

The pipeline works like this: the PDF text is extracted using PyMuPDF, split into 500-word overlapping chunks, and converted to 384-dimensional vectors using sentence-transformers. Those vectors are stored in a FAISS index. When a user asks a question, it's converted to the same vector space, FAISS finds the 5 most similar chunks using L2 distance, and those chunks plus the question are sent to Claude AI which answers based only on that context.

I deployed it as a Docker container on Hugging Face Spaces.

---

## 11. What to Add Next (Future Improvements)

1. **Support more file types** — DOCX, TXT, web URLs
2. **Chat history** — remember previous questions in the same session
3. **Multiple documents** — upload 5 PDFs and compare them
4. **Source citations** — show exactly which part of the PDF the answer came from
5. **Persistent storage** — use PostgreSQL + pgvector instead of in-memory FAISS
6. **User authentication** — let users have accounts and save their documents
7. **Streaming responses** — show the answer word by word as Claude generates it

---

*Documentation written by Venkata Ghantasala — May 2026*
