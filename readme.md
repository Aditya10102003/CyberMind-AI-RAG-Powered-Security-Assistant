# 🛡️ CyberMind AI  
## AI-Powered Security Knowledge Assistant

CyberMind AI is a Retrieval-Augmented Generation (RAG) based cybersecurity knowledge assistant that allows users to upload security documents and interact with them using natural language.

The system combines semantic search, keyword-based retrieval, and Large Language Models to provide accurate, context-aware answers with document sources and confidence scores.

---

# 🚀 Features

## 📄 Document Intelligence

- Upload multiple documents
- Supported formats:
  - PDF
  - DOCX
  - TXT
  - CSV
  - PPTX
- Automatic document loading and processing
- Intelligent text chunking

---

## 🔍 Advanced Retrieval System

CyberMind AI uses a hybrid retrieval approach:

### Semantic Search

- HuggingFace Sentence Transformers embeddings
- FAISS vector database
- Similarity-based document retrieval

### Keyword Search

- BM25 ranking algorithm
- Improves retrieval for exact security terminology

### Hybrid Retrieval

Combines both approaches to improve answer accuracy.

---

## 🤖 Generative AI

Powered by:

- Groq Llama 3.3 70B Versatile
- LangChain
- Retrieval-Augmented Generation (RAG)

The model answers only from retrieved document context to reduce hallucination.

---

## 🔐 Authentication

Implemented secure API authentication:

- User registration
- Login system
- JWT token authentication
- Protected document upload and question endpoints

---

## 📚 Source Citations

Every generated response includes:

- Document name
- Page number
- Relevant text preview

Users can verify where the answer was generated from.

---

## 📊 Confidence Scoring

Each response provides:

- Confidence level
- Confidence percentage

Example:


🟢 Confidence: High (100%)


---

# 🏗️ Architecture


            User
             |
             |
    Streamlit Interface
             |
             |
      FastAPI Backend
             |
    -----------------
    |               |

Authentication RAG Pipeline
| |
JWT Document Processing
|
Text Chunking
|
-----------------
| |
FAISS Search BM25
| |
-----------------
|
Retrieved Context
|
Groq Llama 3.3
|
Answer
|
Sources + Confidence


---

# 🛠️ Tech Stack

## Backend

- FastAPI
- Uvicorn
- JWT Authentication

## AI / ML

- LangChain
- FAISS
- HuggingFace Embeddings
- Groq Llama 3.3 70B

## Search

- FAISS Vector Search
- BM25 Keyword Retrieval

## Frontend

- Streamlit

## Programming

- Python

---

# 📂 Project Structure



CyberMindAI/

│
├── api.py # FastAPI backend
├── app.py # Streamlit application
├── requirements.txt
│
├── utils/
│ ├── auth.py # JWT authentication
│ ├── rag.py # Retrieval and generation pipeline
│ ├── loader.py # Document loading
│ ├── chunker.py # Text chunking
│ ├── embeddings.py # Embedding model
│ ├── vector_store.py # FAISS database
│ ├── bm25.py # Keyword retrieval
│ ├── llm.py # LLM client
│ ├── language.py # Language support
│ └── voice.py # Voice features
│
└── .streamlit/
└── config.toml


---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/Aditya10102003/CyberMind-AI-RAG-Powered-Security-Assistant.git

cd CyberMind-AI-RAG-Powered-Security-Assistant

Install dependencies:

pip install -r requirements.txt
🔑 Environment Variables

Create a .env file:

GROQ_API_KEY=your_groq_api_key
▶️ Running the Application
Start Streamlit UI
streamlit run app.py
Start FastAPI Backend
uvicorn api:app --reload
🔗 API Endpoints
Register User
POST /register

Example:

{
 "username":"aditya",
 "password":"password123"
}
Login
POST /login

Returns JWT access token.

Upload Documents
POST /upload

Requires:

Authorization: Bearer <token>

Uploads documents and creates knowledge base.

Ask Questions
POST /ask

Example:

{
 "question":"Explain SQL injection"
}

Returns:

Answer
Confidence score
Source citations
🔮 Future Improvements
Persistent FAISS storage
Database-backed user management
Role-based access control
Cloud deployment
Conversation memory
Advanced security document analytics
👨‍💻 Author

Aditya Yadav

Cybersecurity | Generative AI | RAG Applications

GitHub:
https://github.com/Aditya10102003


After replacing it:

```bash
git add README.md
git commit -m "Update README with complete CyberMind AI architecture"
git push origin main

This README will actually make the project look like a real AI security product, not just a college demo. It will also help during interviews.