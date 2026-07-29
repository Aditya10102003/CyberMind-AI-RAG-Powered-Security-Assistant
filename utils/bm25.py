from rank_bm25 import BM25Okapi


def create_bm25_index(chunks):
    """
    Create a BM25 index from document chunks.
    """

    tokenized_chunks = [
        doc.page_content.lower().split()
        for doc in chunks
    ]

    bm25 = BM25Okapi(tokenized_chunks)

    return bm25

def bm25_search(bm25, chunks, query, k=5):
    """
    Search BM25 and return (document, score).
    """

    tokenized_query = query.lower().split()

    scores = bm25.get_scores(tokenized_query)

    ranked_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )[:k]

    return [
        (chunks[i], scores[i])
        for i in ranked_indices
    ]