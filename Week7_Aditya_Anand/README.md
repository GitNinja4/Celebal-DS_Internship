# AI Document Assistant (RAG)

## Project Overview

AI Document Assistant is a Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and interact with them through a conversational chat interface. The system uses semantic search to retrieve relevant document chunks and a large language model (Google Gemini) to generate accurate, context-aware answers.

---

## Features

> *(Placeholders — to be implemented in upcoming weeks)*

- [ ] Upload and process PDF documents
- [ ] Chunk and embed document content into a vector store
- [ ] Semantic similarity search over uploaded documents
- [ ] Conversational Q&A powered by Google Gemini
- [ ] Multi-document support
- [ ] Chat history persistence
- [ ] Settings panel for model and chunking configuration

---

## Tech Stack

| Layer             | Technology                        |
|-------------------|-----------------------------------|
| UI Framework      | Streamlit                         |
| LLM               | Google Gemini (`google-generativeai`) |
| Embeddings        | Sentence Transformers             |
| Vector Store      | FAISS (CPU)                       |
| Orchestration     | LangChain                         |
| PDF Parsing       | PyMuPDF / PyPDF                   |
| Text Splitting    | LangChain Text Splitters          |
| Environment       | python-dotenv                     |
| Language          | Python 3.10+                      |

---

## Folder Structure

```
Week7_Aditya_Anand/
│
├── app.py                  # Streamlit entry point
├── requirements.txt        # Project dependencies
├── .env                    # API keys (not committed)
├── .gitignore
│
├── rag/                    # Core RAG pipeline modules
│   ├── __init__.py
│   ├── pdf_loader.py       # PDF ingestion
│   ├── chunker.py          # Text chunking
│   ├── embedder.py         # Embedding generation
│   ├── vector_store.py     # FAISS vector store management
│   ├── retriever.py        # Semantic retrieval
│   ├── generator.py        # LLM response generation
│   └── pipeline.py         # End-to-end RAG pipeline
│
├── pages/                  # Streamlit multi-page app
│   ├── chat.py             # Chat interface page
│   ├── documents.py        # Document management page
│   └── settings.py         # Settings & configuration page
│
├── uploads/                # User-uploaded PDF files
├── vector_db/              # Persisted FAISS index
├── assets/                 # Static assets
│   ├── logo.png
│   └── styles.css
│
├── utils/                  # Utility helpers
│   ├── __init__.py
│   └── helpers.py
│
└── chat_history/           # Persisted chat sessions
```

---

## Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd Week7_Aditya_Anand

# 2. Create and activate virtual environment
python -m venv venv

# Windows (CMD)
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Edit .env and replace 'your_api_key_here' with your actual Google API key

# 5. Run the application
streamlit run app.py
```

---

## Future Roadmap

- **Week 8** — Implement PDF loading, chunking, and embedding pipeline
- **Week 9** — Build FAISS vector store and semantic retriever
- **Week 10** — Integrate Google Gemini for response generation
- **Week 11** — Build Streamlit UI (chat, documents, settings pages)
- **Week 12** — Add chat history, multi-document support, and polish

---

*Built by Aditya Anand — Celebal Technologies Data Science Internship*
