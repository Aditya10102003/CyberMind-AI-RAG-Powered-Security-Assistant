import os
from typing import List
from fastapi import FastAPI, UploadFile, File
from utils.loader import load_document
from utils.chunker import chunk_documents
from utils.embeddings import get_embedding_model
from utils.vector_store import create_vector_store
from utils.bm25 import create_bm25_index

from utils.rag import (
    retrieve_documents,
    generate_sources,
    generate_answer_api
)

from utils.llm import get_llm, get_groq_client
#from utils.groq_client import get_groq_client

from pydantic import BaseModel
from utils.auth import get_current_user
from utils.auth import (
    hash_password,
    verify_password,
    create_access_token
)


app = FastAPI(
    title="CyberMind AI API",
    version="1.0"
)

vector_store = None
bm25 = None
chunks = None
uploaded_files = []
users = {}

class QuestionRequest(BaseModel):

    question: str

class UserRequest(BaseModel):

    username: str

    password: str

@app.get("/")
def home():

    return {

        "message": "Welcome to CyberMind AI API",

        "status": "running"

    }

from fastapi import Depends
@app.post("/upload")
async def upload_documents(

    files: List[UploadFile] = File(...),

    current_user: str = Depends(get_current_user)

):

    global vector_store
    global bm25
    global chunks
    global uploaded_files

    os.makedirs("data", exist_ok=True)

    all_documents = []
    uploaded_names = []

    for file in files:

        save_path = os.path.join(
            "data",
            file.filename
        )

        uploaded_names.append(file.filename)

        with open(save_path, "wb") as f:

            f.write(await file.read())

        documents = load_document(save_path)

        all_documents.extend(documents)

    chunks = chunk_documents(all_documents)

    embedding_model = get_embedding_model()

    vector_store = create_vector_store(
        chunks,
        embedding_model
    )

    bm25 = create_bm25_index(chunks)

    uploaded_files = uploaded_names

    return {

        "message": "Knowledge base created successfully",

        "documents_uploaded": len(uploaded_files),

        "chunks_created": len(chunks)

    }
@app.post("/register")
def register(
    user: UserRequest
):

    if user.username in users:

        return {
            "message": "User already exists"
        }

    users[user.username] = hash_password(
        user.password
    )

    return {
        "message": "Registration successful"
    }

@app.post("/login")
def login(
    user: UserRequest
):

    if user.username not in users:

        return {
            "message": "Invalid username or password"
        }

    hashed_password = users[user.username]

    if not verify_password(
        user.password,
        hashed_password
    ):

        return {
            "message": "Invalid username or password"
        }

    token = create_access_token(
        {
            "sub": user.username
        }
    )

    return {

        "access_token": token,

        "token_type": "bearer"

    }

@app.post("/ask")
async def ask_question(

    request: QuestionRequest,

    current_user: str = Depends(get_current_user)

):

    global vector_store
    global bm25
    global chunks

    if vector_store is None:

        return {
            "error": "Please upload documents first."
        }

    client = get_groq_client()

    history = []

    retrieved_docs, results, bm25_results = retrieve_documents(
        vector_store,
        bm25,
        chunks,
        request.question
    )

    if not retrieved_docs:

        return {

            "answer": (
                "I couldn't find this information "
                "in the uploaded document."
            ),

            "sources": [],

            "confidence": "Low",

            "confidence_value": 0

        }

    answer = generate_answer_api(
        retrieved_docs,
        history,
        request.question,
        client
    )

    sources = generate_sources(
        retrieved_docs
    )

    confidence = "High"
    confidence_value = 100

    return {

        "answer": answer,

        "confidence": confidence,

        "confidence_value": confidence_value,

        "sources": sources

    }
    
