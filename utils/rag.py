import os
from utils.bm25 import bm25_search

FETCH_K = 10
DEFAULT_K = 5
RELATIVE_MARGIN = 0.35


def retrieve_documents(
    vector_store,
    bm25,
    chunks,
    search_query
):
    """
    Retrieve relevant chunks using
    Hybrid Search (FAISS + BM25).
    """

    results = vector_store.similarity_search_with_score(
        search_query,
        k=FETCH_K
    )

    bm25_results = bm25_search(
        bm25,
        chunks,
        search_query,
        k=FETCH_K
    )

    if results:

        best_score = min(
            score for _, score in results
        )

        cutoff = (
            best_score
            + (
                RELATIVE_MARGIN
                * max(best_score, 1e-6)
            )
        )

        filtered = [

            (doc, score)

            for doc, score in results

            if score <= cutoff
        ]

    else:

        filtered = []

    filtered = (
        filtered[:DEFAULT_K]
        if filtered
        else results[:DEFAULT_K]
    )

    faiss_docs = [
        doc for doc, _ in filtered
    ]

    retrieved_docs = []

    seen = set()

    for doc in faiss_docs:

        key = (
            doc.metadata.get("source"),
            doc.metadata.get("page")
        )

        if key not in seen:

            seen.add(key)

            retrieved_docs.append(doc)

    for doc, score in bm25_results:

        key = (
            doc.metadata.get("source"),
            doc.metadata.get("page")
        )

        if key not in seen:

            seen.add(key)

            retrieved_docs.append(doc)

    retrieved_docs = retrieved_docs[:DEFAULT_K]

    return (
        retrieved_docs,
        results,
        bm25_results
    )


def generate_sources(retrieved_docs):

    sources = []
    seen = set()

    for doc in retrieved_docs:

        page = doc.metadata.get(
            "page",
            "Unknown"
        )

        if page != "Unknown":
            page += 1

        source = os.path.basename(
            doc.metadata.get(
                "source",
                "Document"
            )
        )

        key = (
            source,
            page
        )

        if key not in seen:

            seen.add(key)

            sources.append({

                "source": source,

                "page": page,

                "preview":
                    doc.page_content[:250]
                    + "..."

            })

    return sources

def generate_answer(
    retrieved_docs,
    history,
    question,
    client
):
    """
    Generate an answer using the retrieved documents.
    """

    context = "\n\n".join(
        f"[Chunk {i+1}]\n{doc.page_content}"
        for i, doc in enumerate(retrieved_docs)
    )

    conversation_history = ""

    for msg in history:

        role = msg["role"].capitalize()

        conversation_history += (
            f"{role}: {msg['content']}\n"
        )

    prompt = f"""
You are CyberMind AI.

Rules:

1. Answer ONLY using facts present in the Retrieved Context below.

2. Use the conversation history only to understand what a follow-up question is referring to — never pull facts from history that aren't backed by the Retrieved Context.

3. Never invent information, infer beyond what's stated, or fill gaps with general knowledge.

4. If the retrieved context does not contain the answer, say exactly:
"I couldn't find this information in the uploaded document."

5. When multiple chunks are relevant, synthesize across them rather than only using the first one.

Conversation History:

{conversation_history}

Retrieved Context:

{context}

Current Question:

{question}
"""

    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        stream=True
    )

    return stream
def generate_answer_api(
    retrieved_docs,
    history,
    question,
    client
):
    """
    Generate an answer using the retrieved documents.
    """

    context = "\n\n".join(
        f"[Chunk {i+1}]\n{doc.page_content}"
        for i, doc in enumerate(retrieved_docs)
    )

    conversation_history = ""

    for msg in history:

        role = msg["role"].capitalize()

        conversation_history += (
            f"{role}: {msg['content']}\n"
        )

    prompt = f"""
You are CyberMind AI.

Rules:

1. Answer ONLY using facts present in the Retrieved Context below.

2. Use the conversation history only to understand what a follow-up question is referring to — never pull facts from history that aren't backed by the Retrieved Context.

3. Never invent information, infer beyond what's stated, or fill gaps with general knowledge.

4. If the retrieved context does not contain the answer, say exactly:
"I couldn't find this information in the uploaded document."

5. When multiple chunks are relevant, synthesize across them rather than only using the first one.

Conversation History:

{conversation_history}

Retrieved Context:

{context}

Current Question:

{question}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        stream=False
    )

    return response.choices[0].message.content