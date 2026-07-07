# 🛡️ CyberMind AI

## Overview

CyberMind AI is a Retrieval-Augmented Generation (RAG) application that enables users to upload PDF documents and ask natural language questions. The application retrieves semantically relevant content using FAISS and generates context-aware responses using Google Gemini.

---

## Features

- PDF Upload
- Semantic Chunking
- HuggingFace Embeddings
- FAISS Vector Search
- Google Gemini Integration
- Chat Interface
- Source Citations
- Cached Models

---

## Tech Stack

- Python
- Streamlit
- LangChain
- FAISS
- HuggingFace
- Google Gemini

---

## Architecture

User
↓
Upload PDF
↓
PyPDFLoader
↓
Chunking
↓
Embeddings
↓
FAISS
↓
Similarity Search
↓
Gemini
↓
Answer

---


## Installation

pip install -r requirements.txt

streamlit run app.py
