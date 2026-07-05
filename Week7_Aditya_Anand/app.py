"""
AI Document Assistant - Streamlit Entry Point
Phase 2: UI Layout (no RAG logic yet)
Developer: Aditya Anand
"""

import streamlit as st

# ─────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Branding
        st.markdown("## 📚 AI Document Assistant")
        st.divider()

        # Navigation (display only — routing to be wired in later phases)
        st.markdown("**Navigation**")
        st.markdown("• Chat")
        st.markdown("• Documents")
        st.markdown("• Settings")
        st.divider()

        # System Status
        st.markdown("**System Status**")
        st.success("✅ Gemini API")
        st.success("✅ FAISS Vector DB")
        st.success("✅ Embedding Model")
        st.divider()

        # Project Information
        st.markdown("**Project Information**")
        st.markdown("**Version:** v1.0")
        st.markdown("**Developer:** Aditya Anand")


# ─────────────────────────────────────────────
# LEFT COLUMN — Upload & Document Info
# ─────────────────────────────────────────────
def render_upload_section():
    # Upload Document container
    with st.container(border=True):
        st.subheader("📄 Upload Document")
        uploaded_file = st.file_uploader(
            label="Choose a PDF file",
            type=["pdf"],
            help="Upload a PDF document to index and query.",
        )

        if uploaded_file is None:
            st.info("No PDF uploaded.")

    # Document Information container
    with st.container(border=True):
        st.subheader("📋 Document Information")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Filename:**")
            st.markdown("**Pages:**")
            st.markdown("**Size:**")
            st.markdown("**Status:**")
        with col_b:
            st.markdown("—")
            st.markdown("—")
            st.markdown("—")
            st.markdown("⏳ Waiting for upload")

    return uploaded_file


# ─────────────────────────────────────────────
# RIGHT COLUMN — System Overview & Workflow
# ─────────────────────────────────────────────
def render_system_overview():
    # System Overview container
    with st.container(border=True):
        st.subheader("🖥️ System Overview")

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric(label="Documents Indexed", value=0)
        with col_b:
            st.metric(label="Total Chunks", value=0)

        st.divider()

        st.markdown("**Embedding Model:** MiniLM")
        st.markdown("**Vector Store:** FAISS")
        st.markdown("**LLM:** Gemini")

    # Workflow container
    with st.container(border=True):
        st.subheader("🔄 Workflow")

        pipeline_steps = [
            "📤 Upload PDF",
            "📝 Extract Text",
            "✂️ Chunk Text",
            "🔢 Generate Embeddings",
            "🗄️ Store in FAISS",
            "❓ Ask Questions",
            "🔍 Retrieve Context",
            "💬 Generate Answer",
        ]

        for i, step in enumerate(pipeline_steps):
            st.markdown(step)
            if i < len(pipeline_steps) - 1:
                st.markdown("<p style='margin:0; color:gray;'>↓</p>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN PAGE
# ─────────────────────────────────────────────
def main():
    render_sidebar()

    # Hero section
    st.title("📚 AI Document Assistant")
    st.markdown(
        "##### Chat with your PDFs using Retrieval-Augmented Generation (RAG)"
    )
    st.divider()

    # Two-column layout: 70 / 30 split
    left_col, right_col = st.columns([0.7, 0.3])

    with left_col:
        render_upload_section()

    with right_col:
        render_system_overview()


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()
