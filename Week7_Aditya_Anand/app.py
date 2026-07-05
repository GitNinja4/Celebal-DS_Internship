"""
AI Document Assistant - Streamlit Entry Point
Phase 3 (upgraded): Multi-PDF upload and document library.
Developer: Aditya Anand
"""

import streamlit as st
import pandas as pd
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
# SESSION STATE INIT
# ─────────────────────────────────────────────
def init_session_state() -> None:
    """
    Initialise persistent session state keys on first load.
    Rebuilds the document library from disk so it survives page refreshes.
    """
    if "doc_library" not in st.session_state:
        # dict keyed by filename → metadata dict, rebuilt from uploads/ on startup
        loader = PDFLoader()
        existing = loader.get_all_uploaded_docs()
        st.session_state["doc_library"] = {
            doc["filename"]: doc for doc in existing
        }


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar() -> None:
    """Sidebar: branding, navigation, uploaded doc list, system status, info."""
    with st.sidebar:
        st.markdown("## 📚 AI Document Assistant")
        st.divider()

        # ── Navigation ────────────────────────
        st.markdown("**Navigation**")
        st.markdown("• Chat")

        # Documents section with live file list
        st.markdown("• Documents")
        doc_library: dict = st.session_state.get("doc_library", {})
        if doc_library:
            for fname in doc_library:
                st.markdown(f"  &nbsp;&nbsp;📄 {fname}")
        else:
            st.markdown("  &nbsp;&nbsp;*No documents uploaded yet.*")

        st.markdown("• Settings")
        st.divider()

        # ── System Status ─────────────────────
        st.markdown("**System Status**")
        st.success("✅ Gemini API")
        st.success("✅ FAISS Vector DB")
        st.success("✅ Embedding Model")
        st.divider()

        # ── Project Info ──────────────────────
        st.markdown("**Project Information**")
        st.markdown("**Version:** v1.0")
        st.markdown("**Developer:** Aditya Anand")


# ─────────────────────────────────────────────
# LEFT COLUMN — Upload + Document Library
# ─────────────────────────────────────────────
def render_upload_section() -> None:
    """
    Multi-file uploader, per-file status messages, upload summary,
    and the full Document Library table.
    """
    loader = PDFLoader()

    # ── Upload container ──────────────────────
    with st.container(border=True):
        st.subheader("📄 Upload Documents")

        uploaded_files = st.file_uploader(
            label="Choose one or more PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            help="Select multiple PDFs to upload at once.",
        )

        if not uploaded_files:
            st.info("No PDFs uploaded yet. Select one or more files above.")

    # ── Process every uploaded file ───────────
    if uploaded_files:
        results = loader.save_multiple_files(uploaded_files)

        # Tally outcomes
        n_uploaded  = sum(1 for r in results if r.status == "uploaded")
        n_duplicate = sum(1 for r in results if r.status == "duplicate")
        n_failed    = sum(1 for r in results if r.status == "error")

        # Per-file feedback
        for result in results:
            if result.status == "uploaded":
                st.success(f"✅ **{result.filename}** — saved successfully.")
                # Add to session-state library
                st.session_state["doc_library"][result.filename] = {
                    "filename": result.filename,
                    "size_mb":  result.size_mb,
                    "status":   "Uploaded",
                    "path":     str(result.file_path),
                }
            elif result.status == "duplicate":
                st.warning(f"⚠️ **{result.filename}** — already exists.")
            else:
                st.error(f"❌ **{result.filename}** — {result.message}")

        # ── Upload Summary ─────────────────────
        with st.container(border=True):
            st.subheader("📊 Upload Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("✔ Successfully Uploaded", n_uploaded)
            col2.metric("⚠ Already Exists",        n_duplicate)
            col3.metric("❌ Failed",                n_failed)

    # ── Document Library ──────────────────────
    with st.container(border=True):
        st.subheader("📚 Document Library")

        doc_library: dict = st.session_state.get("doc_library", {})

        if not doc_library:
            st.info("Your document library is empty. Upload PDFs to get started.")
        else:
            # Build a clean display DataFrame
            rows = []
            for doc in doc_library.values():
                rows.append({
                    "Filename":      doc["filename"],
                    "Size (MB)":     doc["size_mb"],
                    "Status":        doc["status"],
                    "Storage Path":  doc["path"],
                })

            df = pd.DataFrame(rows)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Filename":     st.column_config.TextColumn("Filename"),
                    "Size (MB)":    st.column_config.NumberColumn("Size (MB)", format="%.3f"),
                    "Status":       st.column_config.TextColumn("Status"),
                    "Storage Path": st.column_config.TextColumn("Storage Path"),
                },
            )


# ─────────────────────────────────────────────
# RIGHT COLUMN — System Overview & Workflow
# ─────────────────────────────────────────────
def render_system_overview() -> None:
    """System metrics (dynamic doc count) and static RAG workflow pipeline."""

    doc_count = len(st.session_state.get("doc_library", {}))

    # ── System Overview ───────────────────────
    with st.container(border=True):
        st.subheader("🖥️ System Overview")

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric(label="Documents Uploaded", value=doc_count)
        with col_b:
            st.metric(label="Total Chunks", value=0)   # populated in Phase 4

        st.divider()

        st.markdown("**Embedding Model:** MiniLM")
        st.markdown("**Vector Store:** FAISS")
        st.markdown("**LLM:** Gemini")

    # ── Workflow pipeline ─────────────────────
    with st.container(border=True):
        st.subheader("🔄 Workflow")

        pipeline_steps = [
            "📤 Upload PDF",
            "📝 Extract Text",
            "✂️  Chunk Text",
            "🔢 Generate Embeddings",
            "🗄️  Store in FAISS",
            "❓ Ask Questions",
            "🔍 Retrieve Context",
            "💬 Generate Answer",
        ]

        for i, step in enumerate(pipeline_steps):
            st.markdown(step)
            if i < len(pipeline_steps) - 1:
                st.markdown(
                    "<p style='margin:0; color:gray;'>↓</p>",
                    unsafe_allow_html=True,
                )


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main() -> None:
    init_session_state()
    render_sidebar()

    # Hero
    st.title("📚 AI Document Assistant")
    st.markdown(
        "##### Chat with your PDFs using Retrieval-Augmented Generation (RAG)"
    )
    st.divider()

    # 70 / 30 column split
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
