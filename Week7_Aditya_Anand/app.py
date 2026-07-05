"""
AI Document Assistant — Streamlit Entry Point
Dark ChatGPT-style UI. Sidebar: sticky top+bottom, scrollable middle.
Developer: Aditya Anand
"""

from pathlib import Path
import streamlit as st
from rag.pdf_loader import PDFLoader

# ── Page config ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

_CSS_PATH = Path(__file__).parent / "assets" / "styles.css"

# ── CSS injection ────────────────────────────────────────────
def inject_css() -> None:
    if _CSS_PATH.exists():
        st.markdown(
            f"<style>{_CSS_PATH.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )

# ── Session state ────────────────────────────────────────────
def init_session_state() -> None:
    loader = PDFLoader()
    if "doc_library" not in st.session_state:
        st.session_state["doc_library"] = {
            d["filename"]: d for d in loader.get_all_uploaded_docs()
        }
    if "upload_queue"  not in st.session_state:
        st.session_state["upload_queue"]  = []
    if "last_results"  not in st.session_state:
        st.session_state["last_results"]  = []

# ── Helpers ──────────────────────────────────────────────────
def _size_label(mb: float) -> str:
    return f"{mb * 1024:.0f} KB" if mb < 1 else f"{mb:.2f} MB"

def _file_mb(uf) -> float:
    return round(len(uf.getvalue()) / (1024 * 1024), 3)

# ════════════════════════════════════════════════════════════
# SIDEBAR
# The correct ChatGPT pattern inside Streamlit:
#   • Sticky top  → position:sticky; top:0   (brand + actions)
#   • Middle      → plain flow — Streamlit's OWN sidebar scroll handles this
#   • Sticky bot  → position:sticky; bottom:0  (user profile)
# Do NOT set overflow:hidden on the sidebar — that kills scrolling.
# ════════════════════════════════════════════════════════════
def render_sidebar() -> None:
    """
    ChatGPT-style sidebar:
      • First child  → sticky top  (brand + actions)
      • Middle       → scrollable  (nav + live doc list + status)
      • Last child   → sticky bot  (user profile)

    Each zone is ONE st.markdown call so CSS :first-child / :last-child
    can pin them. The middle uses a <div class='sb-scroll-middle'> which
    the CSS gives flex:1 + overflow-y:auto.
    """
    doc_library: dict = st.session_state.get("doc_library", {})
    n = len(doc_library)

    # Build the document rows HTML from live session state
    if doc_library:
        doc_rows_html = "".join(
            f"""<div style="display:flex;align-items:center;gap:9px;
                            padding:8px 10px;border-radius:8px;font-size:0.85rem;
                            color:{'#ffffff' if i==0 else '#c5c5c5'};
                            background:{'#2f2f2f' if i==0 else 'transparent'};
                            font-weight:{'500' if i==0 else '400'};
                            margin-bottom:1px;cursor:pointer;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                  <span style="flex-shrink:0;">📄</span>
                  <span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                      {fname if len(fname)<=26 else fname[:23]+'…'}
                  </span>
                </div>"""
            for i, fname in enumerate(doc_library)
        )
    else:
        doc_rows_html = (
            "<div style='padding:5px 10px 8px;font-size:0.82rem;color:#8e8ea0;'>"
            "No documents yet</div>"
        )

    with st.sidebar:

        # ── 1. STICKY TOP ────────────────────────────────────
        st.markdown(
            """<div style="position:sticky;top:0;z-index:100;
                           background:#171717;padding:16px 6px 10px 6px;
                           border-bottom:1px solid #2a2a2a;">
                 <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                   <div style="width:34px;height:34px;background:#10a37f;border-radius:50%;
                               display:flex;align-items:center;justify-content:center;
                               font-size:1.1rem;flex-shrink:0;">📚</div>
                   <span style="font-size:0.96rem;font-weight:700;color:#ececec;">
                     AI Document Assistant
                   </span>
                 </div>
                 <div style="display:flex;align-items:center;gap:10px;padding:8px 8px;
                             border-radius:8px;font-size:0.87rem;color:#c5c5c5;
                             cursor:pointer;margin-bottom:2px;">
                   <span>✏️</span><span>New Session</span>
                 </div>
                 <div style="display:flex;align-items:center;gap:10px;padding:8px 8px;
                             border-radius:8px;font-size:0.87rem;color:#c5c5c5;
                             cursor:pointer;">
                   <span>🔍</span><span>Search documents</span>
                 </div>
               </div>""",
            unsafe_allow_html=True,
        )

        # ── 2. SCROLLABLE MIDDLE ─────────────────────────────
        st.markdown(
            f"""<div style="padding:8px 6px;">

                  <!-- Navigation -->
                  <div style="font-size:0.70rem;font-weight:600;color:#8e8ea0;
                               text-transform:uppercase;letter-spacing:0.07em;
                               padding:8px 8px 4px 8px;">Navigation</div>
                  <div style="display:flex;align-items:center;gap:9px;
                              padding:8px 10px;border-radius:8px;font-size:0.86rem;
                              color:#c5c5c5;margin-bottom:1px;cursor:pointer;">
                    💬 &nbsp;Chat
                  </div>
                  <div style="display:flex;align-items:center;gap:9px;
                              padding:8px 10px;border-radius:8px;font-size:0.86rem;
                              color:#c5c5c5;margin-bottom:1px;cursor:pointer;">
                    ⚙️ &nbsp;Settings
                  </div>

                  <!-- Documents -->
                  <div style="font-size:0.70rem;font-weight:600;color:#8e8ea0;
                               text-transform:uppercase;letter-spacing:0.07em;
                               padding:12px 8px 4px 8px;">
                    📁 Documents
                    <span style="color:#10a37f;margin-left:5px;font-weight:700;">{n}</span>
                  </div>
                  {doc_rows_html}

                  <!-- System Status -->
                  <div style="border-top:1px solid #2a2a2a;margin-top:8px;padding-top:4px;">
                    <div style="font-size:0.70rem;font-weight:600;color:#8e8ea0;
                                 text-transform:uppercase;letter-spacing:0.07em;
                                 padding:8px 8px 4px 8px;">System Status</div>
                    <div style="padding:4px 10px;font-size:0.84rem;color:#a7f3d0;">
                        🟢 Gemini API
                    </div>
                    <div style="padding:4px 10px;font-size:0.84rem;color:#a7f3d0;">
                        🟢 FAISS Vector DB
                    </div>
                    <div style="padding:4px 10px;font-size:0.84rem;color:#a7f3d0;">
                        🟢 Embedding Model
                    </div>
                  </div>

                  <!-- Bottom spacer so sticky-bottom doesn't overlap content -->
                  <div style="height:80px;"></div>
                </div>""",
            unsafe_allow_html=True,
        )

        # ── 3. STICKY BOTTOM ─────────────────────────────────
        st.markdown(
            """<div style="position:sticky;bottom:0;z-index:100;
                           background:#171717;padding:10px 6px 16px 6px;
                           border-top:1px solid #2a2a2a;">
                 <div style="display:flex;align-items:center;gap:10px;
                             padding:7px 8px;border-radius:10px;cursor:pointer;">
                   <div style="width:34px;height:34px;
                               background:linear-gradient(135deg,#10a37f,#0d6efd);
                               border-radius:50%;display:flex;align-items:center;
                               justify-content:center;font-size:0.82rem;
                               font-weight:700;color:#fff;flex-shrink:0;">AA</div>
                   <div style="min-width:0;">
                     <div style="font-size:0.87rem;font-weight:600;color:#ececec;">
                       Aditya Anand
                     </div>
                     <div style="font-size:0.71rem;color:#8e8ea0;margin-top:1px;">
                       v1.0 · Celebal Internship
                     </div>
                   </div>
                 </div>
               </div>""",
            unsafe_allow_html=True,
        )

# ════════════════════════════════════════════════════════════
# UPLOAD PANEL  — two-stage: stage → remove → commit
# ════════════════════════════════════════════════════════════
def render_upload_panel() -> None:
    loader = PDFLoader()

    with st.container(border=True):
        st.markdown("### 📤 Upload Documents")
        st.markdown(
            "<p style='color:#8e8ea0;font-size:0.84rem;margin-top:-6px;'>"
            "Pick PDFs · Remove mistakes · Click Upload</p>",
            unsafe_allow_html=True,
        )

        picked = st.file_uploader(
            "PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        # Merge into queue without duplicates
        if picked:
            existing = {f.name for f in st.session_state["upload_queue"]}
            for f in picked:
                if f.name not in existing:
                    st.session_state["upload_queue"].append(f)
                    existing.add(f.name)

        queue: list = st.session_state["upload_queue"]

        if queue:
            st.markdown(
                f"<p style='color:#8e8ea0;font-size:0.8rem;margin:6px 0 4px;'>"
                f"{len(queue)} file(s) staged</p>",
                unsafe_allow_html=True,
            )

            to_remove: list[int] = []
            for idx, uf in enumerate(queue):
                col_card, col_btn = st.columns([0.88, 0.12])
                with col_card:
                    st.markdown(
                        f"""<div class="queue-chip">
                              <span style="font-size:1.2rem;flex-shrink:0;">📄</span>
                              <span class="chip-name">{uf.name}</span>
                              <span class="chip-size">{_size_label(_file_mb(uf))}</span>
                            </div>""",
                        unsafe_allow_html=True,
                    )
                with col_btn:
                    st.markdown("<div style='margin-top:4px;'></div>", unsafe_allow_html=True)
                    if st.button("✕", key=f"rm_{idx}_{uf.name}", help=f"Remove {uf.name}"):
                        to_remove.append(idx)

            for i in sorted(to_remove, reverse=True):
                st.session_state["upload_queue"].pop(i)
            if to_remove:
                st.rerun()

            col_up, col_clr = st.columns([0.7, 0.3])
            with col_up:
                do_upload = st.button(
                    f"⬆️ Upload {len(queue)} file(s)",
                    type="primary",
                    use_container_width=True,
                )
            with col_clr:
                if st.button("🗑️ Clear All", use_container_width=True):
                    st.session_state["upload_queue"] = []
                    st.session_state["last_results"]  = []
                    st.rerun()

            if do_upload:
                results = loader.save_multiple_files(queue)
                st.session_state["last_results"] = results
                for r in results:
                    if r.status == "uploaded":
                        st.session_state["doc_library"][r.filename] = {
                            "filename": r.filename,
                            "size_mb":  r.size_mb,
                            "status":   "Uploaded",
                            "path":     str(r.file_path),
                        }
                st.session_state["upload_queue"] = []
                st.rerun()
        else:
            st.markdown(
                "<div style='text-align:center;padding:22px 0;color:#8e8ea0;font-size:0.88rem;'>"
                "📂 No files staged. Pick PDFs above.</div>",
                unsafe_allow_html=True,
            )

    # ── Result chips after upload ────────────────────────────
    results = st.session_state.get("last_results", [])
    if results:
        n_ok  = sum(1 for r in results if r.status == "uploaded")
        n_dup = sum(1 for r in results if r.status == "duplicate")
        n_err = sum(1 for r in results if r.status == "error")

        st.markdown("#### Last Upload Results")
        for r in results:
            badge = (
                "<span class='chip-badge-new'>Saved</span>"      if r.status == "uploaded"  else
                "<span class='chip-badge-dupe'>Duplicate</span>"  if r.status == "duplicate" else
                "<span class='chip-badge-err'>Error</span>"
            )
            st.markdown(
                f"""<div class="file-chip">
                      <span class="chip-icon">📄</span>
                      <span class="chip-name">{r.filename}</span>
                      <span class="chip-size">{_size_label(r.size_mb) if r.size_mb else "—"}</span>
                      {badge}
                    </div>""",
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""<div style="display:flex;gap:8px;margin-top:10px;">
                  <div class="summary-card green" style="flex:1;">{n_ok}
                    <div class="card-label">Uploaded</div></div>
                  <div class="summary-card yellow" style="flex:1;">{n_dup}
                    <div class="card-label">Duplicate</div></div>
                  <div class="summary-card red" style="flex:1;">{n_err}
                    <div class="card-label">Failed</div></div>
                </div>""",
            unsafe_allow_html=True,
        )

# ════════════════════════════════════════════════════════════
# DOCUMENT LIBRARY
# ════════════════════════════════════════════════════════════
def render_doc_library() -> None:
    doc_library: dict = st.session_state.get("doc_library", {})

    with st.container(border=True):
        hc, cc = st.columns([0.75, 0.25])
        with hc:
            st.markdown("### 📚 Document Library")
        with cc:
            st.markdown(
                f"<div style='text-align:right;padding-top:6px;color:#10a37f;"
                f"font-weight:700;'>{len(doc_library)} doc(s)</div>",
                unsafe_allow_html=True,
            )

        if not doc_library:
            st.markdown(
                "<div style='text-align:center;padding:28px 0;color:#8e8ea0;font-size:0.88rem;'>"
                "📭 Library empty — upload PDFs above.</div>",
                unsafe_allow_html=True,
            )
            return

        to_delete: list[str] = []
        for doc in doc_library.values():
            cc2, dc = st.columns([0.9, 0.1])
            with cc2:
                st.markdown(
                    f"""<div class="lib-row">
                          <span class="lib-icon">📄</span>
                          <div class="lib-info">
                            <div class="lib-name">{doc['filename']}</div>
                            <div class="lib-meta">
                              {_size_label(doc['size_mb'])} · uploads/{doc['filename']}
                            </div>
                          </div>
                          <span class="lib-badge">✔ {doc['status']}</span>
                        </div>""",
                    unsafe_allow_html=True,
                )
            with dc:
                st.markdown("<div style='margin-top:5px;'></div>", unsafe_allow_html=True)
                if st.button("🗑", key=f"del_{doc['filename']}", help=f"Remove {doc['filename']}"):
                    to_delete.append(doc["filename"])

        for fname in to_delete:
            del st.session_state["doc_library"][fname]
        if to_delete:
            st.rerun()

# ════════════════════════════════════════════════════════════
# RIGHT PANEL — System Overview + RAG Pipeline
# ════════════════════════════════════════════════════════════
def render_right_panel() -> None:
    doc_count = len(st.session_state.get("doc_library", {}))

    with st.container(border=True):
        st.markdown("### 🖥️ System Overview")
        c1, c2 = st.columns(2)
        c1.metric("Documents", doc_count)
        c2.metric("Chunks", 0)
        st.divider()
        for icon, label, val in [
            ("🧠", "Embedding Model", "MiniLM"),
            ("🗄️",  "Vector Store",   "FAISS"),
            ("✨",  "LLM",            "Gemini"),
        ]:
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;"
                f"padding:4px 0;font-size:0.86rem;'>"
                f"<span style='color:#8e8ea0;'>{icon} {label}</span>"
                f"<span style='color:#10a37f;font-weight:600;'>{val}</span></div>",
                unsafe_allow_html=True,
            )

    with st.container(border=True):
        st.markdown("### 🔄 RAG Pipeline")
        steps = [
            ("📤","Upload PDF"), ("📝","Extract Text"), ("✂️","Chunk Text"),
            ("🔢","Embeddings"), ("🗄️","Store FAISS"),  ("❓","Ask Question"),
            ("🔍","Retrieve"),   ("💬","Generate Answer"),
        ]
        for i, (icon, label) in enumerate(steps):
            st.markdown(
                f"<div class='workflow-step'>{icon}&nbsp;{label}</div>",
                unsafe_allow_html=True,
            )
            if i < len(steps) - 1:
                st.markdown("<div class='workflow-arrow'>↓</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
def main() -> None:
    inject_css()
    init_session_state()
    render_sidebar()

    st.markdown(
        "<h1 style='margin-bottom:0;'>📚 AI Document Assistant</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#8e8ea0;font-size:0.94rem;margin-top:3px;margin-bottom:12px;'>"
        "Chat with your PDFs using Retrieval-Augmented Generation (RAG)</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    left, right = st.columns([0.65, 0.35], gap="large")
    with left:
        render_upload_panel()
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        render_doc_library()
    with right:
        render_right_panel()


if __name__ == "__main__":
    main()
