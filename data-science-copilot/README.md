# 🤖 Autonomous Data Science Co‑Pilot

AI-powered data analysis: upload a dataset, ask in plain English, and receive
Pandas code, executed in a secure sandbox with automatic error repair via RAG,
plus interactive Plotly visualizations.

Developed during the Celebal Technologies Summer Internship 2026.

## Overview

- Upload CSV, Excel, or JSON files.
- Ask natural-language questions about your data.
- The agent generates `Pandas` code and executes it in a sandbox.
- On runtime errors, the system uses a FAISS-backed retriever of Pandas
  documentation to repair code and retry (up to 3 attempts).
- Outputs include textual explanations and interactive Plotly charts.

## Features

- Upload CSV, Excel & JSON datasets
- Natural language queries
- AI-generated Pandas code
- Secure sandbox execution
- Autonomous self-correction (up to 3 retries)
- RAG with Pandas documentation (FAISS)
- Interactive Plotly visualizations
- Transparent agent execution trace

## Architecture

```
Dataset -> User Query -> LLM (Gemini) + LangChain Agent -> generate analyze(df)
        -> Sandbox Execution -> Success: Result & Chart
                              -> Failure: FAISS Retriever -> Docs -> Repair -> Retry
```

## Tech Stack

- LLM: Gemini (via `gemini-flash-latest`)
- Agent: LangChain
- RAG: FAISS + Gemini Embeddings
- Data: Pandas, NumPy
- Charts: Plotly
- UI: Streamlit
- Language: Python

## Project Structure

```
data-science-copilot/
├── agent/          # Code generation, sandbox execution, self-correction loop
├── rag/             # Doc fetching, chunking, embedding, retrieval
├── utils/           # File loading (CSV/Excel/JSON) and chart building
├── sample_data/      # Sample dataset for quick demos
├── app.py            # Streamlit UI
├── requirements.txt
└── README.md
```

## Installation

```bash
git clone <repository-url>
cd data-science-copilot

python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the project root and add your Gemini API key:

```env
GOOGLE_API_KEY=YOUR_API_KEY
```

Get a key at [Google AI Studio](https://aistudio.google.com/apikey).

(Optional but recommended) Verify your key works before going further:

```bash
python test_gemini_connection.py
```

Build the RAG knowledge base (required once, before first run):

```bash
python rag/fetch_docs.py
python rag/build_index.py
```

> Note: `build_index.py` embeds ~400 documentation chunks and respects
> Gemini's free-tier rate limits by processing in small batches. This can
> take several minutes on the first run — this is expected. If interrupted,
> just re-run the same command; it resumes from a local checkpoint instead
> of starting over.

Run the Streamlit app:

```bash
streamlit run app.py
```

## Example Questions

- Which region generated the highest sales?
- Show the monthly sales trend.
- Are there any missing values?
- Which product performs best?
- Compare revenue across categories.

## Highlights

- Autonomous AI agent
- Secure code execution
- Self-healing workflow
- Explainable execution trace
- Interactive dashboards

## Future Improvements

- SQL database support
- Multi-file analysis
- PDF report export
- Docker deployment
- Cloud hosting
- Voice-based queries

## Acknowledgements

Built during the Celebal Technologies Summer Internship 2026.

Special thanks to Google Gemini, LangChain, Pandas, FAISS, Plotly, and Streamlit.

If you found this project useful, consider giving it a star!