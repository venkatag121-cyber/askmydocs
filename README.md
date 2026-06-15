# 📄 AskMyDocs — Chat with any PDF using RAG + Claude AI

> Upload any PDF and ask questions about it in natural language. Built with Retrieval-Augmented Generation (RAG), FAISS vector search, and Claude AI.

**[🚀 Live Demo](https://your-username.hf.space)** · **[📂 GitHub](https://github.com/your-username/askmydocs)**

---

## 🎯 What It Does

Most AI chatbots only know what they were trained on. **AskMyDocs** lets you give the AI YOUR document and ask questions about it — accurately, without hallucination.

Upload a research paper → ask "What methodology did they use?"
Upload a contract → ask "What are the termination clauses?"
Upload a manual → ask "How do I reset the device?"

---

## 🧠 How RAG Works (Simple Version)

```
PDF → Extract Text → Split into Chunks → Convert to Vectors (Embeddings)
                                                    ↓
Question → Convert to Vector → Find Similar Chunks (FAISS Search)
                                                    ↓
                              Relevant Chunks + Question → Claude AI → Answer
```

**Why not just send the whole PDF to the AI?**
LLMs have a token limit (~200k tokens max). A large PDF exceeds that. RAG solves this by only sending the *relevant* parts.

---

## 🛠 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | FastAPI (Python) | Fast async API, great for AI workloads |
| PDF Reading | PyMuPDF (fitz) | Reliable text extraction |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Free, runs locally, good quality |
| Vector DB | FAISS | Facebook's vector search — fast and simple |
| LLM | Claude (claude-sonnet-4) | Best instruction-following, honest about what it doesn't know |
| Frontend | Vanilla HTML/CSS/JS | No build step, fast, deployable anywhere |
| Deploy | Hugging Face Spaces + Docker | Free hosting for AI projects |

---

## 🚀 Run Locally (5 minutes)

### 1. Clone the repo
```bash
git clone https://github.com/your-username/askmydocs.git
cd askmydocs
```

### 2. Set up Python environment
```bash
cd backend
python -m venv venv

# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
# Note: First run downloads the embedding model (~80MB), this is normal.
```

### 4. Add your API key
```bash
cp .env.example .env
# Open .env and replace: ANTHROPIC_API_KEY=your_key_here
# Get your key at: https://console.anthropic.com
```

### 5. Start the server
```bash
uvicorn main:app --reload
# Server runs at: http://localhost:8000
```

### 6. Open the app
Open `frontend/index.html` in your browser, or visit `http://localhost:8000`

---

## 🐳 Run with Docker
```bash
docker build -t askmydocs .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=your_key_here askmydocs
```

---

## ☁️ Deploy Free on Hugging Face Spaces

1. Create account at [huggingface.co](https://huggingface.co)
2. New Space → SDK: Docker → paste this repo
3. Settings → Secrets → add `ANTHROPIC_API_KEY`
4. Your app is live at `https://your-username-askmydocs.hf.space`

---

## 📁 Project Structure

```
askmydocs/
├── backend/
│   ├── main.py            # FastAPI app — all the RAG logic
│   ├── requirements.txt   # Python dependencies
│   └── .env.example       # API key template
├── frontend/
│   └── index.html         # The UI (single file, no build needed)
├── Dockerfile             # Container config for deployment
└── README.md              # You're here
```

---

## 🔧 Key Technical Decisions

**Why FAISS over a hosted vector DB (Pinecone, Weaviate)?**
FAISS runs fully in-memory with no external service needed. Perfect for demos and small-to-medium documents. For production with millions of documents, a hosted DB would be better.

**Why all-MiniLM-L6-v2 for embeddings?**
It's fast, lightweight (~80MB), runs on CPU, and produces good quality embeddings for semantic search. No API calls, no cost.

**Why chunk size 500 with 50 overlap?**
500 words balances context (enough info per chunk) vs. precision (smaller chunks = better search). The 50-word overlap prevents losing context at boundaries.

**What would make this production-ready?**
- Persistent storage (PostgreSQL + pgvector instead of in-memory FAISS)
- User authentication
- Async embedding generation with job queues
- Rate limiting
- Support for more file types (DOCX, TXT, web URLs)

---

## 🙏 License

MIT — free to use, modify, and build on.
