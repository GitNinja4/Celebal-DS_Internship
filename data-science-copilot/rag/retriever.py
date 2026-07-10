"""
Step 4c: The retriever.

Given an error message (from agent/sandbox.py), search the FAISS
index for the most relevant Pandas documentation chunks. This is
the "R" in RAG -- Retrieval.

Step 5 will take these retrieved chunks and hand them to the LLM
so it can generate a corrected version of the failing code.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

INDEX_DIR = os.path.join(os.path.dirname(__file__), "faiss_index")

_vectorstore = None  # loaded once, reused across calls


def _get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
        _vectorstore = FAISS.load_local(
            INDEX_DIR,
            embeddings,
            allow_dangerous_deserialization=True,  # safe: it's our own local index
        )
    return _vectorstore


def retrieve_relevant_docs(error_message: str, k: int = 3) -> list[dict]:
    """
    Searches the FAISS index for the top-k chunks most relevant to
    the given error message (usually a Python traceback).

    Returns a list of dicts: [{"source": ..., "content": ...}, ...]
    """
    vectorstore = _get_vectorstore()

    # We search using the LAST line of the traceback (the actual
    # exception type + message), not the whole traceback -- file
    # paths and line numbers are just noise for semantic search.
    search_query = error_message.strip().split("\n")[-1]

    results = vectorstore.similarity_search(search_query, k=k)

    return [
        {"source": doc.metadata.get("source", "unknown"), "content": doc.page_content}
        for doc in results
    ]


if __name__ == "__main__":
    # Reuse the exact KeyError from Step 3's bad-code test
    fake_error = (
        "Traceback (most recent call last):\n"
        '  File "<string>", line 4, in analyze\n'
        "KeyError: 'Region'"
    )

    print("Searching for docs relevant to this error:\n")
    print(fake_error.split("\n")[-1])
    print()

    results = retrieve_relevant_docs(fake_error, k=3)

    for i, r in enumerate(results, 1):
        print(f"--- Result {i} (from {r['source']}) ---")
        print(r["content"][:300])
        print()