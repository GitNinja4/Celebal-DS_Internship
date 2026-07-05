"""
AI Document Assistant - Streamlit Entry Point
Phase 3: PDF upload and document management.
Developer: Aditya Anand
"""

import streamlit as st
from rag.pdf_loader import PDFLoader

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
    """
    Renders the PDF upload widget and Document Information panel.
    Handles save, duplicate detection, validation errors, and metadata display.
    """
    loader = PDFLoader()

    # ── Upload Document container ──────────────
    with st.container(border=True):
        st.subheader("📄 Upload Document")

        # Streamlit file uploader — PDF only
        uploaded_file = st.file_uploader(
            label="Choose a PDF file",
            type=["pdf"],
            help="Upload a PDF document to index and query.",
        )

        if uploaded_file is None:
            st.info("No PDF uploaded.")

    # ── Process upload when a file is present ──
    metadata = None

    if uploaded_file is not None:
        try:
            # Track filenames saved in this browser session
            if "saved_files" not in st.session_state:
                st.session_state["saved_files"] = set()

            filename_candidate: str = uploaded_file.name
            dest_path = loader.upload_dir / filename_candidate

            # Duplicate: file already on disk (from a previous session or run)
            is_duplicate: bool = dest_path.exists()

            # save_uploaded_file will not overwrite; returns the path either way
            file_path, filename = loader.save_uploaded_file(uploaded_file)

            if is_duplicate:
                st.warning("⚠️ This document already exists. Showing existing file.")
            else:
                st.success("✅ PDF uploaded successfully. Ready for text extraction.")
                st.session_state["saved_files"].add(filename)

            # Fetch metadata for display
            metadata = loader.get_pdf_metadata(file_path)
            metadata["path"] = str(file_path)

        except ValueError as exc:
            # Wrong file type — guards against programmatic misuse
            st.error(f"❌ Invalid file: {exc}")
        except (IOError, FileNotFoundError) as exc:
            st.error(f"❌ File error: {exc}")

    # ── Document Information container ─────────
    with st.container(border=True):
        st.subheader("📋 Document Information")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Filename:**")
            st.markdown("**Pages:**")
            st.markdown("**Size (MB):**")
            st.markdown("**Status:**")
            st.markdown("**Path:**")

        with col_b:
            if metadata:
                st.markdown(metadata["filename"])
                st.markdown("—")          # Page count added in Phase 4
                st.markdown(str(metadata["size_mb"]))
                st.markdown(f"✅ {metadata['status']}")
                st.markdown(f"`{metadata['path']}`")

                st.info("📌 PDF uploaded successfully. Ready for text extraction.")
            else:
                st.markdown("—")
                st.markdown("—")
                st.markdown("—")
                st.markdown("⏳ Waiting for upload")
                st.markdown("—")

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
