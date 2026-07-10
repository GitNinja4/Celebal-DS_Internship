"""
Step 6c: The Streamlit UI.

Run with:
    streamlit run app.py

This is the actual product: upload a file, ask a question in plain
English, and see the agent write code, execute it, self-correct on
errors (visibly, via the Agent Trace tab), and return a chart + insight.
"""

import os
import streamlit as st
import pandas as pd

from agent.orchestrator import run_agent
from utils.file_loader import load_dataframe, UnsupportedFileError, FileParsingError
from utils.chart_builder import build_chart

st.set_page_config(
    page_title="Autonomous Data Science Co-Pilot",
    layout="wide",
)

# --- Minimal custom styling so this doesn't look like default Streamlit ---
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    h1 { font-weight: 700; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 6px 6px 0 0;
        padding: 8px 16px;
    }
    code { font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Autonomous Data Science Co-Pilot")
st.caption(
    "Upload a CSV, Excel, or JSON file, ask a question in plain English, "
    "and the agent writes and runs the analysis for you — self-correcting "
    "on errors using RAG over the official Pandas documentation."
)

# --- Session state setup ---
if "df" not in st.session_state:
    st.session_state.df = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# --- Data source: sample data or user upload ---
st.subheader("1. Choose your data")

data_source = st.radio(
    "Data source",
    ["📁 Upload my own file", "🧪 Try with sample data"],
    horizontal=True,
    label_visibility="collapsed",
)

if data_source == "🧪 Try with sample data":
    sample_path = os.path.join(os.path.dirname(__file__), "sample_data", "monthly_sales.csv")
    st.session_state.df = pd.read_csv(sample_path)
    st.info(
        "Using **sample_data/monthly_sales.csv** — monthly sales by region and "
        "product, including one deliberately messy value to show off self-correction."
    )
else:
    uploaded_file = st.file_uploader(
        "Upload a data file",
        type=["csv", "xlsx", "xls", "json"],
    )

    if uploaded_file is not None:
        try:
            st.session_state.df = load_dataframe(uploaded_file)
            st.success(f"Loaded '{uploaded_file.name}' — "
                       f"{st.session_state.df.shape[0]} rows, "
                       f"{st.session_state.df.shape[1]} columns.")
        except (UnsupportedFileError, FileParsingError) as e:
            st.error(str(e))
            st.session_state.df = None

df = st.session_state.df

if df is not None:
    with st.expander("Preview data", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)
        st.caption(f"Columns: {', '.join(df.columns.astype(str))}")

    st.divider()
    st.subheader("2. Ask anything about your data")

    if "question_input" not in st.session_state:
        st.session_state.question_input = ""

    example_questions = [
        "Which region has the highest total sales?",
        "What is the total sales per region?",
        "Which product sold the most units?",
        "Is there any missing or messy data in this file?",
    ]

    st.caption("Try an example, or type your own question below:")
    chip_cols = st.columns(len(example_questions))
    for col, eq in zip(chip_cols, example_questions):
        if col.button(eq, use_container_width=True):
            st.session_state.question_input = eq

    question = st.text_input(
        "Ask a question about your data",
        key="question_input",
        placeholder="e.g. Which region has the highest total sales?",
        label_visibility="collapsed",
    )

    run_clicked = st.button("Analyze", type="primary", disabled=not question)

    if run_clicked:
        with st.spinner("Agent is writing and running code..."):
            result = run_agent(df, question)
        st.session_state.last_result = result

    result = st.session_state.last_result

    if result is not None:
        st.divider()
        result_tab, trace_tab = st.tabs(["📊 Result", "🔍 Agent Trace"])

        with result_tab:
            if result["success"]:
                final = result["result"]

                answer = final.get("result")
                st.subheader("Answer")
                if isinstance(answer, pd.DataFrame):
                    st.dataframe(answer, use_container_width=True)
                else:
                    st.write(answer)

                chart_type = final.get("chart_type", "none")
                chart_data = final.get("chart_data")
                fig = build_chart(chart_type, chart_data)
                if fig is not None:
                    st.subheader("Chart")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(
                    "The agent couldn't produce a working answer after "
                    "multiple attempts. Check the Agent Trace tab to see "
                    "exactly what went wrong."
                )

        with trace_tab:
            st.caption(
                "Every attempt the agent made — including failures, the "
                "documentation it retrieved to self-correct, and the final "
                "working code."
            )
            for attempt in result["attempts"]:
                status_icon = "✅" if attempt["outcome"] == "success" else "❌"
                with st.expander(
                    f"{status_icon} Attempt {attempt['attempt_number']} — {attempt['outcome']}",
                    expanded=(attempt["attempt_number"] == len(result["attempts"])),
                ):
                    st.code(attempt["code"], language="python")

                    if attempt["outcome"] == "error":
                        st.markdown("**Error:**")
                        st.code(attempt["error"], language="text")

                        if attempt.get("retrieved_docs"):
                            st.markdown("**Retrieved documentation used to self-correct:**")
                            for doc in attempt["retrieved_docs"]:
                                st.markdown(f"*From `{doc['source']}`:*")
                                st.text(doc["content"][:400] + "...")
else:
    st.info("Upload a CSV, Excel, or JSON file to get started.")