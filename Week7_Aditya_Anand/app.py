"""
AI Document Assistant — RAG System
ChatGPT-style UI: dark, minimal, centered.
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

_CSS = Path(__file__).parent / "assets" / "styles.css"


# ════════════════════════════════════════════════════════════
# Bootstrap
# ════════════════════════════════════════════════════════════
def _css():
    if _CSS.exists():
        st.markdown(f"<style>{_CSS.read_text(encoding='utf-8')}</style>",
                    unsafe_allow_html=True)


def _init():
    loader = PDFLoader()
    if "doc_library" not in st.session_state:
        st.session_state["doc_library"] = {
            d["filename"]: d for d in loader.get_all_uploaded_docs()
        }
    for key in ("upload_queue", "last_results", "active_view"):
        if key not in st.session_state:
            st.session_state[key] = [] if key != "active_view" else "home"


# ════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════
def _sz(mb: float) -> str:
    return f"{mb*1024:.0f} KB" if mb < 1 else f"{mb:.2f} MB"


def _fmb(uf) -> float:
    return round(len(uf.getvalue()) / (1024 * 1024), 3)


# ════════════════════════════════════════════════════════════
# SIDEBAR  — sticky top + scrollable middle + sticky bottom
# ════════════════════════════════════════════════════════════
def sidebar():
    docs: dict = st.session_state.get("doc_library", {})
    n = len(docs)

    # Build doc list HTML
    doc_html = "".join(
        f"""<div style="display:flex;align-items:center;gap:8px;padding:7px 10px;
                        border-radius:8px;font-size:.84rem;
                        color:{'#fff' if i==0 else '#b4b4b4'};
                        background:{'#2f2f2f' if i==0 else 'transparent'};
                        margin-bottom:1px;cursor:pointer;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
                        transition:background .15s;"
             onmouseover="if(this.style.background!='#2f2f2f')this.style.background='#242424'"
             onmouseout="if(this.style.background!='#2f2f2f')this.style.background='transparent'">
              <span style="flex-shrink:0;font-size:.9rem;">📄</span>
              <span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                  {f if len(f)<=24 else f[:21]+'…'}
              </span>
            </div>"""
        for i, f in enumerate(docs)
    ) if docs else "<div style='padding:6px 10px;font-size:.81rem;color:#666;'>No documents yet</div>"

    with st.sidebar:
        # ── Sticky top ──────────────────────────────────────
        st.markdown(
            """<div style="position:sticky;top:0;z-index:200;background:#171717;
                           padding:14px 10px 10px;border-bottom:1px solid #2a2a2a;">

              <!-- Brand -->
              <div style="display:flex;align-items:center;gap:9px;margin-bottom:12px;">
                <div style="width:32px;height:32px;background:#10a37f;border-radius:8px;
                            display:flex;align-items:center;justify-content:center;
                            font-size:1rem;flex-shrink:0;">📚</div>
                <span style="font-size:.94rem;font-weight:700;color:#ececec;
                             white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                  AI Doc Assistant
                </span>
              </div>

              <!-- New Session -->
              <div style="display:flex;align-items:center;gap:9px;padding:8px 10px;
                          border-radius:8px;font-size:.85rem;color:#c5c5c5;
                          cursor:pointer;margin-bottom:2px;
                          border:1px solid #2e2e2e;transition:background .15s;"
                   onmouseover="this.style.background='#242424'"
                   onmouseout="this.style.background='transparent'">
                <span>✏️</span><span>New Session</span>
              </div>

              <!-- Search -->
              <div style="display:flex;align-items:center;gap:9px;padding:8px 10px;
                          border-radius:8px;font-size:.85rem;color:#c5c5c5;
                          cursor:pointer;transition:background .15s;"
                   onmouseover="this.style.background='#242424'"
                   onmouseout="this.style.background='transparent'">
                <span>🔍</span><span>Search documents</span>
              </div>
            </div>""",
            unsafe_allow_html=True,
        )

        # ── Scrollable middle ───────────────────────────────
        st.markdown(
            f"""<div style="padding:10px 10px 4px;">

              <!-- Nav section -->
              <div style="font-size:.68rem;font-weight:600;color:#666;text-transform:uppercase;
                           letter-spacing:.07em;padding:6px 4px 4px;">Navigation</div>

              <div style="display:flex;align-items:center;gap:9px;padding:7px 10px;
                          border-radius:8px;font-size:.85rem;color:#c5c5c5;
                          cursor:pointer;margin-bottom:1px;"
                   onmouseover="this.style.background='#242424'"
                   onmouseout="this.style.background='transparent'">
                💬 &nbsp;Chat
              </div>
              <div style="display:flex;align-items:center;gap:9px;padding:7px 10px;
                          border-radius:8px;font-size:.85rem;color:#c5c5c5;
                          cursor:pointer;margin-bottom:1px;"
                   onmouseover="this.style.background='#242424'"
                   onmouseout="this.style.background='transparent'">
                📁 &nbsp;Documents
              </div>
              <div style="display:flex;align-items:center;gap:9px;padding:7px 10px;
                          border-radius:8px;font-size:.85rem;color:#c5c5c5;
                          cursor:pointer;"
                   onmouseover="this.style.background='#242424'"
                   onmouseout="this.style.background='transparent'">
                ⚙️ &nbsp;Settings
              </div>

              <!-- Documents section -->
              <div style="font-size:.68rem;font-weight:600;color:#666;text-transform:uppercase;
                           letter-spacing:.07em;padding:14px 4px 4px;">
                Uploaded Documents
                <span style="color:#10a37f;margin-left:4px;font-weight:700;">{n}</span>
              </div>
              {doc_html}

              <!-- Status section -->
              <div style="border-top:1px solid #2a2a2a;margin-top:10px;padding-top:6px;">
                <div style="font-size:.68rem;font-weight:600;color:#666;text-transform:uppercase;
                             letter-spacing:.07em;padding:4px 4px 4px;">Status</div>
                <div style="display:flex;align-items:center;gap:8px;padding:5px 10px;
                            font-size:.83rem;color:#a7f3d0;">
                  <span style="color:#10a37f;">●</span> Gemini API
                </div>
                <div style="display:flex;align-items:center;gap:8px;padding:5px 10px;
                            font-size:.83rem;color:#a7f3d0;">
                  <span style="color:#10a37f;">●</span> FAISS Ready
                </div>
                <div style="display:flex;align-items:center;gap:8px;padding:5px 10px;
                            font-size:.83rem;color:#a7f3d0;">
                  <span style="color:#10a37f;">●</span> Embeddings OK
                </div>
              </div>

              <!-- Spacer so sticky bottom doesn't overlap last item -->
              <div style="height:72px;"></div>
            </div>""",
            unsafe_allow_html=True,
        )

        # ── Sticky bottom ───────────────────────────────────
        st.markdown(
            """<div style="position:sticky;bottom:0;z-index:200;background:#171717;
                           padding:10px 10px 14px;border-top:1px solid #2a2a2a;">
              <div style="display:flex;align-items:center;gap:10px;padding:7px 8px;
                          border-radius:10px;cursor:pointer;transition:background .15s;"
                   onmouseover="this.style.background='#242424'"
                   onmouseout="this.style.background='transparent'">
                <div style="width:32px;height:32px;
                            background:linear-gradient(135deg,#10a37f,#1d4ed8);
                            border-radius:50%;display:flex;align-items:center;
                            justify-content:center;font-size:.8rem;font-weight:700;
                            color:#fff;flex-shrink:0;">AA</div>
                <div style="min-width:0;">
                  <div style="font-size:.85rem;font-weight:600;color:#ececec;">Aditya Anand</div>
                  <div style="font-size:.70rem;color:#666;margin-top:1px;">Celebal DS Internship</div>
                </div>
              </div>
            </div>""",
            unsafe_allow_html=True,
        )


# ════════════════════════════════════════════════════════════
# HOME VIEW  — centered, clean, ChatGPT-style
# ════════════════════════════════════════════════════════════
def view_home():
    loader = PDFLoader()

    # ── Centered welcome header ──────────────────────────────
    st.markdown(
        """<div style="text-align:center;padding:3rem 1rem 1.5rem;">
             <div style="font-size:2.1rem;font-weight:700;color:#ececec;
                         margin-bottom:.4rem;">What can I help with?</div>
             <div style="font-size:.97rem;color:#8e8ea0;">
               Upload PDFs · Ask questions · Get AI-powered answers
             </div>
           </div>""",
        unsafe_allow_html=True,
    )

    # ── Centered upload bar ──────────────────────────────────
    _, mid, _ = st.columns([1, 2.5, 1])
    with mid:
        with st.container(border=True):
            picked = st.file_uploader(
                "Drop PDFs here or click to browse",
                type=["pdf"],
                accept_multiple_files=True,
                label_visibility="visible",
            )
            if picked:
                existing = {f.name for f in st.session_state["upload_queue"]}
                for f in picked:
                    if f.name not in existing:
                        st.session_state["upload_queue"].append(f)
                        existing.add(f.name)

        # Queue & actions
        queue: list = st.session_state["upload_queue"]
        if queue:
            st.markdown(
                f"<div style='font-size:.8rem;color:#8e8ea0;margin:8px 0 4px;'>"
                f"  {len(queue)} file(s) staged</div>",
                unsafe_allow_html=True,
            )
            to_rm = []
            for idx, uf in enumerate(queue):
                c1, c2 = st.columns([0.88, 0.12])
                with c1:
                    st.markdown(
                        f"""<div class="file-chip">
                              <span class="chip-icon">📄</span>
                              <span class="chip-name">{uf.name}</span>
                              <span class="chip-size">{_sz(_fmb(uf))}</span>
                            </div>""",
                        unsafe_allow_html=True,
                    )
                with c2:
                    st.markdown("<div style='margin-top:4px;'></div>", unsafe_allow_html=True)
                    if st.button("✕", key=f"rm_{idx}_{uf.name}",
                                 help=f"Remove {uf.name}"):
                        to_rm.append(idx)

            for i in sorted(to_rm, reverse=True):
                st.session_state["upload_queue"].pop(i)
            if to_rm:
                st.rerun()

            ca, cb = st.columns([.7, .3])
            with ca:
                if st.button(f"⬆️  Upload {len(queue)} file(s)",
                             type="primary", use_container_width=True):
                    results = loader.save_multiple_files(queue)
                    st.session_state["last_results"] = results
                    for r in results:
                        if r.status == "uploaded":
                            st.session_state["doc_library"][r.filename] = {
                                "filename": r.filename, "size_mb": r.size_mb,
                                "status": "Uploaded", "path": str(r.file_path),
                            }
                    st.session_state["upload_queue"] = []
                    st.rerun()
            with cb:
                if st.button("🗑  Clear", use_container_width=True):
                    st.session_state["upload_queue"] = []
                    st.session_state["last_results"] = []
                    st.rerun()

    # ── Quick-action chips ───────────────────────────────────
    st.markdown(
        """<div style="display:flex;gap:10px;justify-content:center;
                       flex-wrap:wrap;margin:1.2rem 0 2rem;">
             <div class="action-chip">📄 Upload PDF</div>
             <div class="action-chip">💬 Ask a question</div>
             <div class="action-chip">📊 Summarize document</div>
             <div class="action-chip">🔍 Search content</div>
           </div>""",
        unsafe_allow_html=True,
    )

    # ── Upload results ───────────────────────────────────────
    results = st.session_state.get("last_results", [])
    if results:
        n_ok  = sum(1 for r in results if r.status == "uploaded")
        n_dup = sum(1 for r in results if r.status == "duplicate")
        n_err = sum(1 for r in results if r.status == "error")

        _, m2, _ = st.columns([1, 2.5, 1])
        with m2:
            st.markdown("**Last upload results**")
            for r in results:
                badge = (
                    "<span class='chip-badge-new'>Saved</span>"
                    if r.status == "uploaded" else
                    "<span class='chip-badge-dupe'>Duplicate</span>"
                    if r.status == "duplicate" else
                    "<span class='chip-badge-err'>Error</span>"
                )
                st.markdown(
                    f"""<div class="file-chip">
                          <span class="chip-icon">📄</span>
                          <span class="chip-name">{r.filename}</span>
                          <span class="chip-size">{_sz(r.size_mb) if r.size_mb else '—'}</span>
                          {badge}
                        </div>""",
                    unsafe_allow_html=True,
                )
            st.markdown(
                f"""<div class="summary-row">
                      <div class="s-card green">{n_ok}<div class="s-card-label">Uploaded</div></div>
                      <div class="s-card yellow">{n_dup}<div class="s-card-label">Duplicate</div></div>
                      <div class="s-card red">{n_err}<div class="s-card-label">Failed</div></div>
                    </div>""",
                unsafe_allow_html=True,
            )


# ════════════════════════════════════════════════════════════
# DOCUMENTS VIEW
# ════════════════════════════════════════════════════════════
def view_documents():
    docs: dict = st.session_state.get("doc_library", {})

    st.markdown(
        f"""<div class="section-hdr">
              <h3>📚 Document Library</h3>
              <span class="badge">{len(docs)} document(s)</span>
            </div>""",
        unsafe_allow_html=True,
    )

    if not docs:
        st.markdown(
            """<div style="text-align:center;padding:3rem;color:#8e8ea0;">
                 <div style="font-size:2.5rem;margin-bottom:1rem;">📭</div>
                 <div style="font-size:1rem;">No documents yet.</div>
                 <div style="font-size:.85rem;margin-top:.4rem;">Upload PDFs from the home screen.</div>
               </div>""",
            unsafe_allow_html=True,
        )
        return

    to_del = []
    for doc in docs.values():
        c1, c2 = st.columns([.92, .08])
        with c1:
            st.markdown(
                f"""<div class="lib-row">
                      <span class="lib-icon">📄</span>
                      <div class="lib-info">
                        <div class="lib-name">{doc['filename']}</div>
                        <div class="lib-meta">{_sz(doc['size_mb'])} · uploads/{doc['filename']}</div>
                      </div>
                      <span class="lib-badge">✔ {doc['status']}</span>
                    </div>""",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown("<div style='margin-top:5px;'></div>", unsafe_allow_html=True)
            if st.button("🗑", key=f"del_{doc['filename']}",
                         help=f"Remove {doc['filename']}"):
                to_del.append(doc["filename"])

    for f in to_del:
        del st.session_state["doc_library"][f]
    if to_del:
        st.rerun()


# ════════════════════════════════════════════════════════════
# SYSTEM VIEW  (right rail info, shown inline below main)
# ════════════════════════════════════════════════════════════
def view_system():
    doc_count = len(st.session_state.get("doc_library", {}))

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        with st.container(border=True):
            st.markdown("### 🖥️ System Overview")
            m1, m2 = st.columns(2)
            m1.metric("Documents", doc_count)
            m2.metric("Chunks", 0)
            st.divider()
            for icon, label, val in [
                ("🧠", "Embedding", "MiniLM"),
                ("🗄️",  "Vector DB",  "FAISS"),
                ("✨",  "LLM",        "Gemini"),
            ]:
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;"
                    f"padding:4px 0;font-size:.86rem;'>"
                    f"<span style='color:#8e8ea0;'>{icon} {label}</span>"
                    f"<span style='color:#10a37f;font-weight:600;'>{val}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    with col2:
        with st.container(border=True):
            st.markdown("### 🔄 RAG Pipeline")
            steps = [
                ("📤","Upload PDF"), ("📝","Extract Text"), ("✂️","Chunk"),
                ("🔢","Embed"),      ("🗄️","Store FAISS"),  ("❓","Query"),
                ("🔍","Retrieve"),   ("💬","Generate"),
            ]
            for i, (ic, lb) in enumerate(steps):
                st.markdown(
                    f"<div class='wf-step'>{ic}&nbsp;{lb}</div>",
                    unsafe_allow_html=True,
                )
                if i < len(steps) - 1:
                    st.markdown("<div class='wf-arrow'>↓</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════
def main():
    _css()
    _init()
    sidebar()

    # Tab navigation (replaces the old column layout)
    tab_home, tab_docs, tab_system = st.tabs(
        ["🏠 Home", "📚 Documents", "⚙️ System"]
    )

    with tab_home:
        view_home()

    with tab_docs:
        st.markdown("<div style='padding:1rem 0;'></div>", unsafe_allow_html=True)
        view_documents()

    with tab_system:
        st.markdown("<div style='padding:1rem 0;'></div>", unsafe_allow_html=True)
        view_system()


if __name__ == "__main__":
    main()
