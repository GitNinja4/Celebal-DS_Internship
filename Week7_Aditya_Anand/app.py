"""
AI Document Assistant — Streamlit Entry Point
Modern dark ChatGPT-style UI with multi-PDF upload queue + remove support.
Developer: Aditya Anand
"""

from pathlib import Path
import streamlit as st
from rag.pdf_loader import PDFLoader

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# INJECT CSS
# ─────────────────────────────────────────────
_CSS_PATH = Path(__file__).parent / "assets" / "styles.css"

def inject_css() -> None:
    """Load and inject the custom stylesheet into the Streamlit page."""
    if _CSS_PATH.exists():
        css = _CSS_PATH.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
def init_session_state() -> None:
    """
    Seed persistent session keys on first load.
    doc_library  — dict[filename → metadata] rebuilt from uploads/ on startup.
    upload_queue — list of filenames staged by the user but not yet committed.
    """
    loader = PDFLoader()

    if "doc_library" not in st.session_state:
        existing = loader.get_all_uploaded_docs()
        st.session_state["doc_library"] = {
            doc["filename"]: doc for doc in existing
        }

    if "upload_queue" not in st.session_state:
        # Stores the raw UploadedFile objects the user has staged
        st.session_state["upload_queue"] = []

    if "last_results" not in st.session_state:
        # Stores UploadResult list from the most recent commit
        st.session_state["last_results"] = []

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def _size_label(size_mb: float) -> str:
    """Return a human-readable size string."""
    if size_mb < 1:
        return f"{size_mb * 1024:.0f} KB"
    return f"{size_mb:.2f} MB"

def _file_size_mb(uf) -> float:
    """Return the size of a Streamlit UploadedFile in MB."""
    return round(len(uf.getvalue()) / (1024 * 1024), 3)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar() -> None:
    """
    ChatGPT-style sidebar:
      TOP    — brand + actions  (pinned, never scrolls)
      MIDDLE — nav + doc list   (scrolls on overflow)
      BOTTOM — user profile     (pinned at bottom)

    Layout achieved by injecting a wrapper div via CSS that targets
    Streamlit's own sidebar content block, combined with individual
    st.markdown calls for each section — avoids the HTML-stripping
    issue Streamlit applies to large injected HTML blobs.
    """
    doc_library: dict = st.session_state.get("doc_library", {})
    doc_count = len(doc_library)

    with st.sidebar:

        # ── TOP: Brand ────────────────────────────────────────
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:10px;
                        padding:18px 4px 4px 4px;margin-bottom:4px;">
                <div style="width:34px;height:34px;background:#10a37f;border-radius:50%;
                            display:flex;align-items:center;justify-content:center;
                            font-size:1.1rem;flex-shrink:0;">📚</div>
                <span style="font-size:1rem;font-weight:700;color:#ececec;">
                    AI Document Assistant
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── TOP: Action buttons ───────────────────────────────
        st.markdown(
            """
            <div style="margin-bottom:2px;">
                <div style="display:flex;align-items:center;gap:10px;
                            padding:9px 8px;border-radius:8px;font-size:0.88rem;
                            color:#c5c5c5;cursor:pointer;transition:background 0.15s;"
                     onmouseover="this.style.background='#2a2a2a'"
                     onmouseout="this.style.background='transparent'">
                    <span style="width:20px;text-align:center;">✏️</span>
                    <span>New Session</span>
                </div>
                <div style="display:flex;align-items:center;gap:10px;
                            padding:9px 8px;border-radius:8px;font-size:0.88rem;
                            color:#c5c5c5;cursor:pointer;"
                     onmouseover="this.style.background='#2a2a2a'"
                     onmouseout="this.style.background='transparent'">
                    <span style="width:20px;text-align:center;">🔍</span>
                    <span>Search documents</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<hr style='border:none;border-top:1px solid #2a2a2a;margin:8px 0;'/>",
            unsafe_allow_html=True,
        )

        # ── MIDDLE: Nav items ─────────────────────────────────
        st.markdown(
            """
            <div style="font-size:0.72rem;font-weight:600;color:#8e8ea0;
                        text-transform:uppercase;letter-spacing:0.06em;
                        padding:4px 8px 6px 8px;">Navigation</div>
            <div style="display:flex;align-items:center;gap:9px;
                        padding:8px 10px;border-radius:8px;font-size:0.86rem;
                        color:#c5c5c5;margin-bottom:1px;cursor:pointer;">
                💬 &nbsp; Chat
            </div>
            <div style="display:flex;align-items:center;gap:9px;
                        padding:8px 10px;border-radius:8px;font-size:0.86rem;
                        color:#c5c5c5;margin-bottom:1px;cursor:pointer;">
                ⚙️ &nbsp; Settings
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── MIDDLE: Document list — scrollable section ────────
        st.markdown(
            f"""
            <div style="font-size:0.72rem;font-weight:600;color:#8e8ea0;
                        text-transform:uppercase;letter-spacing:0.06em;
                        padding:12px 8px 6px 8px;">
                📁 Documents
                <span style="color:#10a37f;font-weight:700;margin-left:4px;">
                    {doc_count}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # The document list lives in a scrollable container
        # max-height keeps it bounded; bottom sections stay visible
        if doc_library:
            doc_rows = "".join(
                f"""<div style="display:flex;align-items:center;gap:9px;
                                padding:7px 10px;border-radius:8px;font-size:0.84rem;
                                color:#c5c5c5;white-space:nowrap;overflow:hidden;
                                text-overflow:ellipsis;margin-bottom:1px;
                                {'background:#2f2f2f;color:#fff;' if i == 0 else ''}
                                cursor:pointer;">
                        <span style="flex-shrink:0;">📄</span>
                        <span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                            {fname if len(fname) <= 28 else fname[:25] + '…'}
                        </span>
                    </div>"""
                for i, fname in enumerate(doc_library)
            )
            st.markdown(
                f"""<div style="max-height:220px;overflow-y:auto;overflow-x:hidden;
                               padding-right:2px;margin-bottom:4px;">
                        {doc_rows}
                    </div>""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div style='padding:6px 10px 10px;font-size:0.82rem;color:#8e8ea0;'>"
                "No documents uploaded yet</div>",
                unsafe_allow_html=True,
            )

        # ── MIDDLE: System Status ─────────────────────────────
        st.markdown(
            "<hr style='border:none;border-top:1px solid #2a2a2a;margin:8px 0;'/>",
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div style="font-size:0.72rem;font-weight:600;color:#8e8ea0;
                        text-transform:uppercase;letter-spacing:0.06em;
                        padding:4px 8px 6px 8px;">System Status</div>
            <div style="padding:5px 10px;font-size:0.84rem;color:#a7f3d0;">
                🟢 &nbsp;Gemini API
            </div>
            <div style="padding:5px 10px;font-size:0.84rem;color:#a7f3d0;">
                🟢 &nbsp;FAISS Vector DB
            </div>
            <div style="padding:5px 10px;font-size:0.84rem;color:#a7f3d0;">
                🟢 &nbsp;Embedding Model
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── BOTTOM: User profile — pushed to bottom with spacer ──
        # st.empty() + CSS margin-top:auto equivalent using a spacer
        st.markdown("<div style='flex:1;min-height:20px;'></div>", unsafe_allow_html=True)
        st.markdown(
            "<hr style='border:none;border-top:1px solid #2a2a2a;margin:8px 0 10px 0;'/>",
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:10px;
                        padding:8px 8px 16px 8px;cursor:pointer;border-radius:10px;">
                <div style="width:34px;height:34px;
                            background:linear-gradient(135deg,#10a37f,#0d6efd);
                            border-radius:50%;display:flex;align-items:center;
                            justify-content:center;font-size:0.85rem;font-weight:700;
                            color:#fff;flex-shrink:0;">AA</div>
                <div style="min-width:0;">
                    <div style="font-size:0.88rem;font-weight:600;color:#ececec;">
                        Aditya Anand
                    </div>
                    <div style="font-size:0.72rem;color:#8e8ea0;margin-top:1px;">
                        v1.0 · Celebal Internship
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────
# UPLOAD QUEUE PANEL
# ─────────────────────────────────────────────
def render_upload_panel() -> None:
    """
    Two-stage upload flow:
      Stage 1 — file picker builds a queue shown as cards with ✕ remove buttons.
      Stage 2 — "Upload X files" button commits the queue to disk.
    """
    loader = PDFLoader()

    with st.container(border=True):
        st.markdown("### 📤 Upload Documents")
        st.markdown(
            "<p style='color:#8e8ea0;font-size:0.85rem;margin-top:-8px;'>"
            "Select PDFs · Remove mistakes · Then click Upload</p>",
            unsafe_allow_html=True,
        )

        # ── File picker ────────────────────────
        picked = st.file_uploader(
            label="Choose PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        # Merge newly picked files into the queue (no duplicates by name)
        if picked:
            existing_names = {f.name for f in st.session_state["upload_queue"]}
            for f in picked:
                if f.name not in existing_names:
                    st.session_state["upload_queue"].append(f)
                    existing_names.add(f.name)

        queue: list = st.session_state["upload_queue"]

        # ── Queue cards with remove buttons ────
        if queue:
            st.markdown(
                f"<p style='color:#8e8ea0;font-size:0.82rem;"
                f"margin-bottom:6px;'>{len(queue)} file(s) staged</p>",
                unsafe_allow_html=True,
            )

            to_remove = []

            # Scrollable queue list — caps at 240px then scrolls internally
            st.markdown(
                "<div style='max-height:240px;overflow-y:auto;overflow-x:hidden;"
                "padding-right:4px;margin-bottom:8px;'>",
                unsafe_allow_html=True,
            )

            for idx, uf in enumerate(queue):
                size_mb = _file_size_mb(uf)
                col_card, col_btn = st.columns([0.88, 0.12])

                with col_card:
                    st.markdown(
                        f"""<div class='queue-chip'>
                            <span style='font-size:1.3rem;'>📄</span>
                            <span class='chip-name'>{uf.name}</span>
                            <span class='chip-size'>{_size_label(size_mb)}</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )

                with col_btn:
                    # Vertically centre the button beside the card
                    st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
                    if st.button("✕", key=f"remove_{idx}_{uf.name}", help=f"Remove {uf.name}"):
                        to_remove.append(idx)

            # Apply removals (reverse order to keep indices valid)
            # Close scrollable queue wrapper first
            st.markdown("</div>", unsafe_allow_html=True)

            for idx in sorted(to_remove, reverse=True):
                st.session_state["upload_queue"].pop(idx)
            if to_remove:
                st.rerun()

            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

            # ── Commit button ───────────────────
            col_up, col_clear = st.columns([0.7, 0.3])
            with col_up:
                do_upload = st.button(
                    f"⬆️  Upload {len(queue)} file(s)",
                    type="primary",
                    use_container_width=True,
                )
            with col_clear:
                if st.button("🗑️ Clear All", use_container_width=True):
                    st.session_state["upload_queue"] = []
                    st.session_state["last_results"]  = []
                    st.rerun()

            if do_upload:
                results = loader.save_multiple_files(queue)
                st.session_state["last_results"] = results

                # Persist new files to doc_library
                for r in results:
                    if r.status == "uploaded":
                        st.session_state["doc_library"][r.filename] = {
                            "filename": r.filename,
                            "size_mb":  r.size_mb,
                            "status":   "Uploaded",
                            "path":     str(r.file_path),
                        }

                # Clear queue after commit
                st.session_state["upload_queue"] = []
                st.rerun()

        else:
            st.markdown(
                "<div style='text-align:center;padding:24px 0;"
                "color:#8e8ea0;font-size:0.9rem;'>"
                "📂 No files staged. Pick PDFs above.</div>",
                unsafe_allow_html=True,
            )

    # ── Post-upload result chips ─────────────
    results = st.session_state.get("last_results", [])
    if results:
        n_ok   = sum(1 for r in results if r.status == "uploaded")
        n_dup  = sum(1 for r in results if r.status == "duplicate")
        n_err  = sum(1 for r in results if r.status == "error")

        st.markdown("#### Last Upload Results")

        for r in results:
            if r.status == "uploaded":
                badge = "<span class='chip-badge-new'>Saved</span>"
            elif r.status == "duplicate":
                badge = "<span class='chip-badge-dupe'>Duplicate</span>"
            else:
                badge = "<span class='chip-badge-err'>Error</span>"

            size_str = _size_label(r.size_mb) if r.size_mb else "—"
            st.markdown(
                f"""<div class='file-chip'>
                    <span class='chip-icon'>📄</span>
                    <span class='chip-name'>{r.filename}</span>
                    <span class='chip-size'>{size_str}</span>
                    {badge}
                </div>""",
                unsafe_allow_html=True,
            )

        # Summary bar
        st.markdown(
            f"""<div style='display:flex;gap:10px;margin-top:10px;margin-bottom:4px;'>
                <div class='summary-card green' style='flex:1;'>
                    {n_ok}
                    <div class='card-label'>Uploaded</div>
                </div>
                <div class='summary-card yellow' style='flex:1;'>
                    {n_dup}
                    <div class='card-label'>Duplicate</div>
                </div>
                <div class='summary-card red' style='flex:1;'>
                    {n_err}
                    <div class='card-label'>Failed</div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────
# DOCUMENT LIBRARY
# ─────────────────────────────────────────────
def render_doc_library() -> None:
    """Render all saved PDFs as styled cards with metadata."""
    with st.container(border=True):
        doc_library: dict = st.session_state.get("doc_library", {})

        header_col, count_col = st.columns([0.75, 0.25])
        with header_col:
            st.markdown("### 📚 Document Library")
        with count_col:
            st.markdown(
                f"<div style='text-align:right;padding-top:8px;"
                f"color:#10a37f;font-weight:700;font-size:1rem;'>"
                f"{len(doc_library)} document(s)</div>",
                unsafe_allow_html=True,
            )

        if not doc_library:
            st.markdown(
                "<div style='text-align:center;padding:32px 0;"
                "color:#8e8ea0;font-size:0.9rem;'>"
                "📭 No documents in the library yet.<br>"
                "<span style='font-size:0.8rem;'>Upload PDFs above to get started.</span>"
                "</div>",
                unsafe_allow_html=True,
            )
            return

        # ── Remove-from-library buttons ────────
        to_delete: list[str] = []

        # Scrollable list wrapper — max 340px, then internal scroll
        st.markdown(
            "<div style='max-height:340px;overflow-y:auto;overflow-x:hidden;"
            "padding-right:4px;'>",
            unsafe_allow_html=True,
        )

        for doc in doc_library.values():
            size_str = _size_label(doc["size_mb"])
            short_path = "uploads/" + doc["filename"]

            card_col, del_col = st.columns([0.9, 0.1])
            with card_col:
                st.markdown(
                    f"""<div class='lib-row'>
                        <span class='lib-icon'>📄</span>
                        <div class='lib-info'>
                            <div class='lib-name'>{doc['filename']}</div>
                            <div class='lib-meta'>{size_str} &nbsp;·&nbsp; {short_path}</div>
                        </div>
                        <span class='lib-badge'>✔ {doc['status']}</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
            with del_col:
                st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
                if st.button("🗑", key=f"del_{doc['filename']}", help=f"Remove {doc['filename']} from library"):
                    to_delete.append(doc["filename"])

        # Close the scrollable wrapper
        st.markdown("</div>", unsafe_allow_html=True)

        for fname in to_delete:
            del st.session_state["doc_library"][fname]
        if to_delete:
            st.rerun()

# ─────────────────────────────────────────────
# RIGHT PANEL — Stats + Workflow
# ─────────────────────────────────────────────
def render_right_panel() -> None:
    doc_count = len(st.session_state.get("doc_library", {}))

    # ── Stats ─────────────────────────────────
    with st.container(border=True):
        st.markdown("### 🖥️ System Overview")

        c1, c2 = st.columns(2)
        c1.metric("Documents", doc_count)
        c2.metric("Chunks", 0)   # Phase 4

        st.divider()

        items = [
            ("🧠", "Embedding Model", "MiniLM"),
            ("🗄️", "Vector Store",    "FAISS"),
            ("✨", "LLM",             "Gemini"),
        ]
        for icon, label, value in items:
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;"
                f"padding:4px 0;font-size:0.87rem;'>"
                f"<span style='color:#8e8ea0;'>{icon} {label}</span>"
                f"<span style='color:#10a37f;font-weight:600;'>{value}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── RAG Pipeline ──────────────────────────
    with st.container(border=True):
        st.markdown("### 🔄 RAG Pipeline")

        steps = [
            ("📤", "Upload PDF"),
            ("📝", "Extract Text"),
            ("✂️",  "Chunk Text"),
            ("🔢", "Generate Embeddings"),
            ("🗄️",  "Store in FAISS"),
            ("❓", "Ask Questions"),
            ("🔍", "Retrieve Context"),
            ("💬", "Generate Answer"),
        ]

        for i, (icon, label) in enumerate(steps):
            st.markdown(
                f"<div class='workflow-step'>{icon}&nbsp; {label}</div>",
                unsafe_allow_html=True,
            )
            if i < len(steps) - 1:
                st.markdown(
                    "<div class='workflow-arrow'>↓</div>",
                    unsafe_allow_html=True,
                )

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main() -> None:
    inject_css()
    init_session_state()
    render_sidebar()

    # ── Hero (fixed at top, outside the scrollable columns) ──
    st.markdown(
        "<h1 style='margin-bottom:0;padding-bottom:0;'>📚 AI Document Assistant</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#8e8ea0;font-size:0.95rem;margin-top:2px;margin-bottom:10px;'>"
        "Chat with your PDFs using Retrieval-Augmented Generation (RAG)</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # ── Two-column layout ─────────────────────
    # Left (65%) scrolls when content overflows.
    # Right (35%) is sticky — never moves as left grows.
    left, right = st.columns([0.65, 0.35], gap="large")

    with left:
        render_upload_panel()
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        render_doc_library()
        # Bottom padding so last card isn't flush against the scroll boundary
        st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)

    with right:
        render_right_panel()


if __name__ == "__main__":
    main()
