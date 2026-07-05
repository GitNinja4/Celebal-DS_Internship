import streamlit as st

st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="📚",
    layout="wide"
)

# ---------- Sidebar ----------
with st.sidebar:
    st.title("📚 AI Document Assistant")

    st.markdown("---")

    uploaded_files = st.file_uploader(
        "Upload PDF Documents",
        type=["pdf"],
        accept_multiple_files=True
    )

    st.markdown("---")

    st.subheader("System Status")

    st.success("Embedding Model Ready")
    st.success("Vector Database Ready")
    st.success("LLM Ready")

# ---------- Main Page ----------

st.title("📚 AI Document Assistant")
st.caption("Chat with your PDF documents using Retrieval-Augmented Generation (RAG)")

st.markdown("---")

col1, col2 = st.columns([3,1])

with col1:

    st.subheader("💬 Chat")

    question = st.chat_input("Ask a question about your document...")

    if question:
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            st.write("RAG response will appear here...")

with col2:

    st.subheader("📊 Statistics")

    st.metric("Documents", 0)
    st.metric("Chunks", 0)
    st.metric("Questions Asked", 0)

    st.markdown("---")

    st.subheader("Retrieved Chunks")

    st.info("No retrieval yet.")