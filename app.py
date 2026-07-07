import os
import streamlit as st

st.set_page_config(
    page_title="CyberMind AI",
    page_icon="🛡️",
    layout="wide"
)

from utils.loader import load_pdf
from utils.chunker import chunk_documents
from utils.embeddings import get_embedding_model
from utils.vector_store import create_vector_store
from utils.llm import get_llm

# -----------------------------
# Session State Initialization
# -----------------------------
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# Page Configuration
# -----------------------------


st.sidebar.title("🛡️ CyberMind AI")

st.sidebar.markdown("---")

st.sidebar.write("**Embedding Model**")
st.sidebar.write("all-MiniLM-L6-v2")

st.sidebar.write("**LLM**")
st.sidebar.write("Gemini 2.5 Flash")

st.sidebar.write("**Vector Database**")
st.sidebar.write("FAISS")

st.sidebar.markdown("---")

if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.messages.clear()
    st.rerun()

if st.sidebar.button("🆕 New Document"):
    st.session_state.vector_store = None
    st.session_state.uploaded_filename = None
    st.session_state.messages.clear()
    st.rerun()

if st.session_state.vector_store:
    st.sidebar.success("Knowledge Base Ready ✅")
else:
    st.sidebar.warning("Upload a PDF")

st.title("🛡️ CyberMind AI")
st.subheader("AI-Powered Security Knowledge Assistant")

st.divider()

# -----------------------------
# Upload PDF
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload a Security PDF",
    type=["pdf"]
)

if uploaded_file is not None:

    os.makedirs("data", exist_ok=True)
    save_path = os.path.join("data", uploaded_file.name)

    # Only rebuild knowledge base if a different PDF is uploaded
    if st.session_state.uploaded_filename != uploaded_file.name:

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("✅ PDF uploaded successfully!")

        # Load PDF
        documents = load_pdf(save_path)

        # Chunk Documents
        chunks = chunk_documents(documents)

        st.success(f"Total Chunks Created: {len(chunks)}")

       

        # Load Embedding Model
        embedding_model = get_embedding_model()

        # Generate Embedding
        vector = embedding_model.embed_query(chunks[0].page_content)

       

        # Create FAISS Vector Store
        vector_store = create_vector_store(chunks, embedding_model)

        # Save in Session
        st.session_state.vector_store = vector_store
        st.session_state.uploaded_filename = uploaded_file.name

        st.success("✅ Knowledge Base Created Successfully!")

    else:
        st.info("ℹ️ Using existing knowledge base.")


    if st.session_state.uploaded_filename:
        st.sidebar.markdown("---")
        st.sidebar.write("**Current Document**")
        st.sidebar.success(st.session_state.uploaded_filename)

st.divider()

# -----------------------------
# Ask Question
# -----------------------------
# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
question = st.chat_input("Ask a Security Question")

if question:

    if uploaded_file is None:
        st.warning("Please upload a PDF first.")

    elif st.session_state.vector_store is None:
        st.warning("Knowledge base not created.")

    else:

        # Show user message
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.spinner("🧠 Searching knowledge base and generating response..."):

            try:

                retrieved_docs = st.session_state.vector_store.similarity_search(
                    question,
                    k=3
                )

                context = "\n\n".join(
                    [doc.page_content for doc in retrieved_docs]
                )

                prompt = f"""
You are CyberMind AI, an AI assistant specializing in cybersecurity.

Rules:

1. Answer ONLY from the provided context.
2. Do NOT make assumptions or invent information.
3. If the answer is not found, reply:
   "I couldn't find this information in the uploaded document."
4. Keep answers clear and concise.
5. Use bullet points whenever appropriate.
6. If summarizing, organize the answer into sections.

Context:
{context}

Question:
{question}
"""

                llm = get_llm()

                response = llm.invoke(prompt)

                answer = response.content

                with st.chat_message("assistant"):

                    st.markdown(answer)

                    with st.expander("📄 Sources Used"):

                        for i, doc in enumerate(retrieved_docs, start=1):

                            page = doc.metadata.get("page", "Unknown")
                            source = os.path.basename(doc.metadata.get("source", "Document"))

                            st.markdown(f"**📄 {source} | Page {page + 1}**")

                            st.write(doc.page_content)

                            st.divider()

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")