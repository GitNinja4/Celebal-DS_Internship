"""
Step 4b: Build the FAISS vector index from the cached Pandas docs.

Pipeline:
    raw .txt files  -->  chunks  -->  embeddings  -->  FAISS index (saved to disk)

Two important fixes over the previous version:
1. Correct exception handling -- langchain_google_genai wraps Gemini's
   real error in its own GoogleGenerativeAIError class, so we catch
   that (and check the message text) instead of the raw ClientError.
2. Checkpointing -- embeddings are saved to a local JSON file after
   EVERY batch. If the script crashes or gets rate-limited past its
   retries, just run it again -- it skips chunks already embedded
   instead of starting over and wasting API calls.

Usage:
    python rag/build_index.py
"""

import os
import json
import time
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

load_dotenv()

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
INDEX_DIR = os.path.join(os.path.dirname(__file__), "faiss_index")
CHECKPOINT_FILE = os.path.join(os.path.dirname(__file__), "embedding_checkpoint.json")

BATCH_SIZE = 5             # smaller batches = gentler on the rate limit
PAUSE_BETWEEN_BATCHES = 15  # seconds
MAX_RETRIES = 5


def load_and_chunk_docs() -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_chunks: list[Document] = []

    for filename in sorted(os.listdir(DOCS_DIR)):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(DOCS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = splitter.split_text(text)

        for i, chunk in enumerate(chunks):
            all_chunks.append(
                Document(
                    page_content=chunk,
                    metadata={"source": filename, "chunk_index": i},
                )
            )

        print(f"  {filename}: {len(chunks)} chunks")

    return all_chunks


def chunk_key(doc: Document) -> str:
    """Unique ID for a chunk, used to check what's already embedded."""
    return f"{doc.metadata['source']}::{doc.metadata['chunk_index']}"


def load_checkpoint() -> dict:
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_checkpoint(checkpoint: dict):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f)


def embed_batch_with_retry(embeddings, texts: list[str]) -> list[list[float]]:
    """
    Embeds one small batch. Catches the WRAPPED error that
    langchain_google_genai actually raises, checks if it's a rate
    limit by message content, and backs off before retrying.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return embeddings.embed_documents(texts)
        except Exception as e:
            is_rate_limit = "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e)
            if is_rate_limit and attempt < MAX_RETRIES:
                wait_time = 20 * attempt
                print(f"    Rate limited. Waiting {wait_time}s before retry "
                      f"{attempt}/{MAX_RETRIES}...")
                time.sleep(wait_time)
            else:
                raise


def build_index():
    print("Loading and chunking cached docs...")
    chunks = load_and_chunk_docs()
    total = len(chunks)
    print(f"\nTotal chunks across all docs: {total}")

    checkpoint = load_checkpoint()
    if checkpoint:
        print(f"Found existing checkpoint with {len(checkpoint)} chunks already embedded. Resuming...")

    remaining = [doc for doc in chunks if chunk_key(doc) not in checkpoint]
    print(f"Chunks left to embed: {len(remaining)}")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

    for start in range(0, len(remaining), BATCH_SIZE):
        batch_docs = remaining[start:start + BATCH_SIZE]
        batch_texts = [doc.page_content for doc in batch_docs]

        batch_num = start // BATCH_SIZE + 1
        total_batches = (len(remaining) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"  Batch {batch_num}/{total_batches}...")

        batch_vectors = embed_batch_with_retry(embeddings, batch_texts)

        for doc, vector in zip(batch_docs, batch_vectors):
            checkpoint[chunk_key(doc)] = {
                "text": doc.page_content,
                "vector": vector,
                "metadata": doc.metadata,
            }

        save_checkpoint(checkpoint)  # persist after every batch, not just at the end

        if start + BATCH_SIZE < len(remaining):
            time.sleep(PAUSE_BETWEEN_BATCHES)

    print("\nAll chunks embedded. Building FAISS index from checkpoint...")

    text_embedding_pairs = [(v["text"], v["vector"]) for v in checkpoint.values()]
    metadatas = [v["metadata"] for v in checkpoint.values()]

    vectorstore = FAISS.from_embeddings(
        text_embeddings=text_embedding_pairs,
        embedding=embeddings,
        metadatas=metadatas,
    )

    vectorstore.save_local(INDEX_DIR)
    print(f"\nFAISS index saved to: {INDEX_DIR}")
    print("Done. The self-correction retriever can now use this index.")


if __name__ == "__main__":
    build_index()