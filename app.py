import os
import streamlit as st

st.set_page_config(
    page_title="CyberMind AI",
    page_icon="🛡️",
    layout="wide"
)

from utils.loader import load_document
from utils.chunker import chunk_documents
from utils.embeddings import get_embedding_model
from utils.vector_store import create_vector_store
from utils.llm import get_llm, get_groq_client
from utils.bm25 import create_bm25_index, bm25_search
from utils.language import (
    detect_response_language,
    clean_question
)
from streamlit_mic_recorder import mic_recorder


from utils.voice import speech_bytes_to_text
from utils.rag import (
    retrieve_documents,
    generate_sources,
    generate_answer
)

# -----------------------------
# Tunable retrieval settings
# -----------------------------
# NOTE: all-MiniLM-L6-v2 embeddings are NOT normalized by default, so raw
# FAISS L2 distances don't have a fixed "good match" number — an absolute
# threshold (e.g. 1.0) will silently drop correct chunks for some queries
# and keep noise for others. Instead we filter RELATIVE to the best score
# in each batch, which self-calibrates regardless of embedding scale.
RELATIVE_MARGIN = 0.7       # keep chunks within this fraction above the best (lowest) score in the batch
DEFAULT_K = 10
SUMMARY_K = 12
FETCH_K = 20                # candidates fetched before filtering/diversifying
SHOW_DEBUG_SCORES = True    # set False once you've verified retrieval quality

# Words that suggest a question depends on prior conversation turns.
# We only pay for a query-rewrite LLM call when one of these appears —
# most questions are standalone and don't need it.
FOLLOWUP_INDICATORS = [
    "it", "that", "this", "those", "these", "above", "earlier",
    "again", "further", "second", "first", "last", "other", "also",
    "previous", "mentioned",
]

# -----------------------------
# Session State Initialization
# -----------------------------
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "uploaded_filenames" not in st.session_state:
    st.session_state.uploaded_filenames = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "bm25" not in st.session_state:
    st.session_state.bm25 = None

if "chunks" not in st.session_state:
    st.session_state.chunks = None

if "feedback" not in st.session_state:
    st.session_state.feedback = []

if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False
# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("🛡️ CyberMind AI")

st.sidebar.markdown("---")

st.sidebar.write("**Embedding Model**")
st.sidebar.write("all-MiniLM-L6-v2")

st.sidebar.write("**LLM**")
st.sidebar.write("Groq - Llama 3.3 70B Versatile")

st.sidebar.write("**Vector Database**")
st.sidebar.write("FAISS")

st.sidebar.markdown("---")

show_context = st.sidebar.checkbox(
    "Show Retrieved Context",
    value=False
)

if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.messages.clear()
    st.rerun()

if st.sidebar.button("🆕 New Documents"):
    st.session_state.vector_store = None
    st.session_state.uploaded_filenames = []
    st.session_state.messages.clear()
    st.rerun()

if st.sidebar.button("📊 Dashboard"):
    st.session_state.show_dashboard = (
        not st.session_state.show_dashboard
    )


if st.session_state.vector_store:
    st.sidebar.success("Knowledge Base Ready ✅")
else:
    st.sidebar.warning("Upload one or more PDFs")

# -----------------------------
# Main Page
# -----------------------------
st.title("🛡️ CyberMind AI")
st.subheader("AI-Powered Security Knowledge Assistant")


st.divider()

# -----------------------------
# Upload PDF
# -----------------------------
uploaded_files = st.file_uploader(
    "Upload Documents",
    type=[
        "pdf",
        "docx",
        "txt",
        "csv",
        "pptx"
    ],
    accept_multiple_files=True
)

if uploaded_files:

    os.makedirs("data", exist_ok=True)

    all_documents = []
    uploaded_names = []

    for uploaded_file in uploaded_files:

        save_path = os.path.join(
            "data",
            uploaded_file.name
        )

        uploaded_names.append(uploaded_file.name)

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        documents = load_document(save_path)

        all_documents.extend(documents)
    knowledge_base_exists = (
        st.session_state.vector_store is not None
    )
    uploaded_names.sort()
    same_documents = (
        st.session_state.uploaded_filenames == uploaded_names
    )
    if not knowledge_base_exists or not same_documents:

        chunks = chunk_documents(all_documents)

        st.success(f"Total Chunks Created: {len(chunks)}")

        embedding_model = get_embedding_model()

        vector_store = create_vector_store(
            chunks,
            embedding_model
        )

        st.session_state.vector_store = vector_store
        st.session_state.chunks = chunks

        from utils.bm25 import create_bm25_index

        bm25 = create_bm25_index(chunks)

        st.session_state.bm25 = bm25
        st.session_state.uploaded_filenames = uploaded_names

        st.success("✅ Knowledge Base Created Successfully!")

    else:

        st.info("ℹ️ Using existing knowledge base.")

st.sidebar.markdown("---")
st.sidebar.write("**Search Documents**")

selected_documents = st.sidebar.multiselect(

    "Choose documents",

    options=st.session_state.uploaded_filenames,

    default=st.session_state.uploaded_filenames

)
st.divider()

# -----------------------------
# Dashboard
# -----------------------------
if st.session_state.show_dashboard:

    st.header("📊 CyberMind AI Dashboard")

    documents = len(
        st.session_state.uploaded_filenames
    )

    questions = len([
        m
        for m in st.session_state.messages
        if m["role"] == "user"
    ])

    answers = len([
        m
        for m in st.session_state.messages
        if m["role"] == "assistant"
    ])

    # Languages
    languages = set()

    for msg in st.session_state.messages:

        if (
            msg["role"] == "assistant"
            and "language" in msg
        ):

            languages.add(msg["language"])

    # Average Confidence
    confidence_scores = [

        msg["confidence_value"]

        for msg in st.session_state.messages

        if (
            msg["role"] == "assistant"
            and "confidence_value" in msg
        )
    ]

    avg_confidence = (
        int(sum(confidence_scores) / len(confidence_scores))
        if confidence_scores
        else 0
    )

    # Feedback
    helpful = sum(

        1

        for msg in st.session_state.messages

        if msg.get("feedback") == "Helpful"
    )

    not_helpful = sum(

        1

        for msg in st.session_state.messages

        if msg.get("feedback") == "Not Helpful"
    )

    # -----------------------------
# First Row
# -----------------------------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📄 Documents",
            documents
        )

    with col2:
        st.metric(
            "❓ Questions",
            questions
        )

    with col3:
        st.metric(
            "💬 Answers",
            answers
        )

    with col4:
        st.metric(
            "🌍 Languages",
            len(languages)
        )

    # -----------------------------
    # Second Row
    # -----------------------------
    col5, col6, col7 = st.columns(3)

    with col5:
        st.metric(
            "📈 Avg Confidence",
            f"{avg_confidence}%"
        )

    with col6:
        st.metric(
            "👍 Helpful",
            helpful
        )

    with col7:
        st.metric(
            "👎 Not Helpful",
            not_helpful
        )

    st.divider()
    

# -----------------------------
# Display Chat History
# -----------------------------
for i, message in enumerate(
    st.session_state.messages
):

    with st.chat_message(message["role"]):

        if message["role"] == "assistant":

            emoji = {
                "High": "🟢",
                "Medium": "🟡",
                "Low": "🔴"
            }

            if "confidence" in message:

                st.markdown(
                    f"**{emoji[message['confidence']]} Confidence:** "
                    f"{message['confidence']} "
                    f"({message['confidence_value']}%)"
                )

        # Display Answer
        st.markdown(message["content"])

        # -----------------------------
        # Sources
        # -----------------------------
        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):

            st.markdown("### 📄 Sources")

            for src in message["sources"]:

                st.markdown(
                    f"**📄 {src['source']} — Page {src['page']}**"
                )

                st.caption(src["preview"])

                st.divider()

        # -----------------------------
        # Retrieved Context
        # -----------------------------
        if (
            message["role"] == "assistant"
            and show_context
            and message.get("retrieved_context")
        ):

            with st.expander("🔍 Retrieved Context"):

                for j, chunk in enumerate(
                    message["retrieved_context"]
                ):

                    page = chunk["page"]

                    if page != "Unknown":
                        page += 1

                    st.markdown(f"### Chunk {i+1}")

                    st.markdown(
                        f"**Source:** {chunk['source']}"
                    )

                    st.markdown(
                        f"**Page:** {page}"
                    )

                    st.code(
                        chunk["content"],
                        language="text"
                    )

                    st.divider()


        if message["role"] == "assistant":

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "👍 Helpful",
                    key=f"helpful_{i}"
                ):

                    message["feedback"] = "Helpful"

                    st.success("Thank you for your feedback!")

            with col2:

                if st.button(
                    "👎 Not Helpful",
                    key=f"not_helpful_{i}"
                ):

                    message["feedback"] = "Not Helpful"

                    st.success("Thank you for your feedback!")
# -----------------------------
# Helper: rewrite a follow-up question into a standalone query
# -----------------------------
def build_standalone_query(question, history, llm):
    """
    If there's prior conversation, ask the LLM to rewrite the question
    as a standalone query using history for context. This fixes the bug
    where "what about the second one?" gets searched literally, matching
    nothing relevant in the vector store.
    """
    if not history:
        return question

    if not any(word in question.lower().split() for word in FOLLOWUP_INDICATORS):
        # No sign this question depends on prior turns — search with it
        # directly and save an LLM call (and quota).
        return question

    history_text = "\n".join(
        f"{msg['role'].capitalize()}: {msg['content']}"
        for msg in history
    )

    rewrite_prompt = f"""Given this conversation history and a follow-up question, \
rewrite the follow-up as a standalone question that contains all context \
needed to search a document database. If the follow-up is already standalone, \
return it unchanged. Return ONLY the rewritten question, nothing else.

Conversation History:
{history_text}

Follow-up Question:
{question}

Standalone Question:"""

    try:
        rewritten = llm.invoke(rewrite_prompt).content.strip()
        return rewritten if rewritten else question
    except Exception:
        # If rewriting fails for any reason, fall back to the raw question
        # rather than blocking the whole pipeline.
        return question


# -----------------------------
# Chat Input
# -----------------------------

audio = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="⏹️ Stop Recording",
    just_once=True,
    use_container_width=True,
    key="mic"
)
typed_question = st.chat_input("Ask a Security Question")

question = None

if typed_question:
    question = typed_question

elif audio:

    with st.spinner("🎤 Transcribing speech..."):

        question = speech_bytes_to_text(
            audio["bytes"]
        )

    st.success(f"Recognized: {question}")

if question:

    if not uploaded_files:
        st.warning("Please upload a PDF first.")

    elif st.session_state.vector_store is None:
        st.warning("Knowledge base not created.")

    else:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.spinner(
            "🧠 Searching knowledge base and generating response..."
        ):
            language = detect_response_language(question)
            search_query = clean_question(question)
            st.write("Detected Language:", language)

            try:
                llm = get_llm()

                is_summary = any(
                    word in question.lower()
                    for word in ["summary", "summarise", "summarize"]
                )

                # Recent turns BEFORE this question, for follow-up rewriting
                # and for the answer-generation prompt.
                history = st.session_state.messages[-5:-1]

                if is_summary:

                    retrieved_docs = (
                        st.session_state.vector_store.max_marginal_relevance_search(
                            "summary overview main points",
                            k=SUMMARY_K,
                            fetch_k=FETCH_K,

                        )
                    )
                    confidence = "High"
                    confidence_value = 100
                 

                else:
                    language = detect_response_language(question)

                    # Rewrite follow-up questions into standalone queries
                    search_query = build_standalone_query(question, history, llm)

                    # Remove language instructions like "in Tamil"
                    search_query = clean_question(search_query)

                    retrieved_docs, results, bm25_results = retrieve_documents(
                        st.session_state.vector_store,
                        st.session_state.bm25,
                        st.session_state.chunks,
                        search_query
                    )

                    # -----------------------------
                    # Confidence Calculation
                    # -----------------------------
                    confidence = "Low"
                    confidence_value = 0

                    if results:

                        best_score = min(score for _, score in results)

                        confidence_value = max(
                            0,
                            min(
                                100,
                                int((1 / (1 + best_score)) * 100)
                            )
                        )

                        if confidence_value >= 70:
                            confidence = "High"

                        elif confidence_value >= 40:
                            confidence = "Medium"
                if not retrieved_docs:

                    answer = (
                        "I couldn't find this information "
                        "in the uploaded document."
                    )

                    sources = []

                else:
                    client = get_groq_client()

                    answer = ""

                    with st.chat_message("assistant"):

                        response_placeholder = st.empty()

                        stream = generate_answer(
                            retrieved_docs,
                            history,
                            question,
                            client,
                            language=language
                        )

                        for chunk in stream:

                            delta = chunk.choices[0].delta.content

                            if delta:

                                answer += delta

                                response_placeholder.markdown(answer)

                    # Generate citations
                    if "I couldn't find this information" in answer:

                        sources = []

                    else:

                        sources = generate_sources(
                            retrieved_docs
                        )
                # -----------------------------
                # Display Assistant Response
                # -----------------------------

                emoji = {
                    "High": "🟢",
                    "Medium": "🟡",
                    "Low": "🔴"
                }

                st.markdown(
                    f"**{emoji[confidence]} Confidence:** "
                    f"{confidence} ({confidence_value}%)"
                )

                st.markdown(answer)

                if sources:

                    st.markdown("### 📄 Sources")

                    for src in sources:

                        st.markdown(
                            f"**📄 {src['source']} — Page {src['page']}**"
                        )

                        st.caption(src["preview"])

                        st.divider()
                # -----------------------------
                # Save Chat History
                # -----------------------------
                st.session_state.messages.append({

                    "role": "assistant",

                    "content": answer,

                    "sources": sources,

                    "confidence": confidence,

                    "confidence_value": confidence_value,

                    "retrieved_context": (
                        []

                        if "I couldn't find this information" in answer

                        else [

                            {

                                "source": os.path.basename(
                                    doc.metadata.get("source", "Document")
                                ),

                                "page": doc.metadata.get("page", "Unknown"),

                                "content": doc.page_content

                            }

                            for doc in retrieved_docs

                        ]
                    ),

                    "feedback": None,

                    "language": language
                })
            except Exception as e:

                st.error(
                    f"An error occurred: {e}"
                )
