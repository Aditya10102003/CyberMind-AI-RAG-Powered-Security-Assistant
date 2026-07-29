from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_documents(documents):
    """
    Split documents into smaller chunks.
    """

    text_splitter = RecursiveCharacterTextSplitter(
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ],
        chunk_size=700,
        chunk_overlap=150,
        length_function=len
    )

    chunks = text_splitter.split_documents(documents)

    return chunks