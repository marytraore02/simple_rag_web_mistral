"""
RAG Web App — Assistant documentaire avec Mistral.

Interface en 3 onglets :
  📂 Sources   — Upload, prévisualisation et gestion des fichiers
  ⚙️ Pipeline  — Lancement et suivi du pipeline RAG en arrière-plan
  💬 Chat      — Assistant RAG conversationnel

Usage :
    streamlit run streamlit/app.py
"""

from __future__ import annotations

import sys
import time
import shutil
import logging
import base64
from pathlib import Path

import streamlit as st

# ── Chemins ──────────────────────────────────────────────────────────────────
APP_DIR = Path(__file__).parent
ROOT_DIR = APP_DIR.parent
sys.path.insert(0, str(ROOT_DIR))

from config import (
    INPUTS_DIR, MARKDOWN_DIR, FAISS_INDEX_FILE, FAISS_METADATA_FILE,
    AVAILABLE_MODELS, DEFAULT_MODEL, GENERATION_PARAMS,
    SUPPORTED_EXTENSIONS, DOCLING_EXTENSIONS, AUDIO_EXTENSIONS,
    MISTRAL_API_KEY,
)

# ── Configuration Streamlit ───────────────────────────────────────────────────
st.set_page_config(
    page_title="RAG Assistant — Mistral",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personnalisé ──────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Palette & variables ────────────────────────────────── */
:root {
  --bg-dark:     #0d0f14;
  --bg-card:     #161b27;
  --bg-card2:    #1c2232;
  --accent:      #6c63ff;
  --accent2:     #00d4aa;
  --accent3:     #ff6b6b;
  --text-main:   #e8eaf0;
  --text-muted:  #8b92a5;
  --border:      rgba(108,99,255,0.2);
  --radius:      14px;
  --shadow:      0 4px 24px rgba(0,0,0,0.4);
}

/* ── Fond global ─────────────────────────────────────────── */
.stApp {
  background: linear-gradient(135deg, #0d0f14 0%, #111827 60%, #0d1117 100%);
  color: var(--text-main);
  font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* ── Sidebar ─────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
  background: var(--bg-card) !important;
  border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text-main) !important; }

/* ── Onglets ─────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 4px;
  gap: 4px;
  border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
  background: transparent;
  border-radius: 8px;
  color: var(--text-muted);
  font-weight: 500;
  transition: all .2s;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, var(--accent), #9b59f5) !important;
  color: white !important;
}

/* ── Cartes génériques ───────────────────────────────────── */
.rag-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.2rem 1.4rem;
  margin-bottom: 1rem;
  box-shadow: var(--shadow);
}

/* ── En-tête hero ────────────────────────────────────────── */
.hero-header {
  background: linear-gradient(135deg, #1a1f35 0%, #0f1624 100%);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 2rem 2.4rem;
  margin-bottom: 1.5rem;
  text-align: center;
}
.hero-header h1 {
  font-size: 2.4rem;
  font-weight: 800;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
}
.hero-header p { color: var(--text-muted); font-size: 1.05rem; margin: .4rem 0 0; }

/* ── Badge de statut ─────────────────────────────────────── */
.badge {
  display: inline-block;
  padding: .25rem .7rem;
  border-radius: 20px;
  font-size: .78rem;
  font-weight: 700;
  letter-spacing: .05em;
  text-transform: uppercase;
}
.badge-green  { background: rgba(0,212,170,.15); color: #00d4aa; border: 1px solid rgba(0,212,170,.3);}
.badge-yellow { background: rgba(255,190,50,.15); color: #ffc844; border: 1px solid rgba(255,190,50,.3);}
.badge-red    { background: rgba(255,107,107,.15); color: var(--accent3); border: 1px solid rgba(255,107,107,.3);}
.badge-blue   { background: rgba(108,99,255,.15); color: var(--accent); border: 1px solid rgba(108,99,255,.3);}

/* ── Fichiers uploadés ───────────────────────────────────── */
.file-item {
  display: flex;
  align-items: center;
  gap: .7rem;
  background: var(--bg-card2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: .6rem 1rem;
  margin-bottom: .5rem;
  transition: border-color .2s;
}
.file-item:hover { border-color: var(--accent); }
.file-icon { font-size: 1.4rem; }
.file-name { font-weight: 500; flex: 1; color: var(--text-main); }
.file-size { color: var(--text-muted); font-size: .82rem; }

/* ── Messages du chat ────────────────────────────────────── */
div[data-testid="stChatMessage"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  margin-bottom: .6rem !important;
}

/* ── Boutons ─────────────────────────────────────────────── */
div.stButton > button {
  font-weight: 600;
  border-radius: 10px;
  transition: all .2s;
}

/* ── Zone de log / terminal ──────────────────────────────── */
.log-box {
  background: #0a0c12;
  border: 1px solid #2d3148;
  border-radius: 10px;
  padding: 1rem;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: .8rem;
  color: #b8c0d8;
  max-height: 280px;
  overflow-y: auto;
  white-space: pre-wrap;
  line-height: 1.6;
}

/* ── Step tracker ────────────────────────────────────────── */
.step-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: .6rem 1rem;
  border-radius: 10px;
  margin-bottom: .4rem;
  background: var(--bg-card2);
  border: 1px solid var(--border);
  transition: all .3s;
}
.step-row.active  { border-color: var(--accent); background: rgba(108,99,255,.08); }
.step-row.done    { border-color: #00d4aa; background: rgba(0,212,170,.06); }
.step-row.pending { opacity: 0.5; }
.step-num {
  width: 28px; height: 28px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: .85rem;
  background: var(--bg-card); border: 2px solid #3a4060;
  flex-shrink: 0;
}
.step-row.active  .step-num { background: var(--accent); border-color: var(--accent); color: white; }
.step-row.done    .step-num { background: #00d4aa; border-color: #00d4aa; color: #000; }
.step-label { font-weight: 500; flex: 1; }
.step-desc  { color: var(--text-muted); font-size: .82rem; }

/* ── Preview image ───────────────────────────────────────── */
.preview-box {
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  background: var(--bg-card2);
}

/* ── Input chat ──────────────────────────────────────────── */
div[data-testid="stChatInput"] textarea {
  background: var(--bg-card) !important;
  border-color: var(--border) !important;
  color: var(--text-main) !important;
}

/* ── Scrollbar ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2e3555; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def human_size(n_bytes: int) -> str:
    for unit in ("o", "Ko", "Mo", "Go"):
        if n_bytes < 1024:
            return f"{n_bytes:.0f} {unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} To"


def file_icon(suffix: str) -> str:
    s = suffix.lower()
    if s == ".pdf":       return "📕"
    if s == ".docx":      return "📘"
    if s == ".pptx":      return "📊"
    if s == ".xlsx":      return "📗"
    if s in {".html",".htm"}: return "🌐"
    if s in {".png",".jpg",".jpeg",".webp",".tiff",".tif",".bmp"}: return "🖼️"
    if s in {".wav",".mp3",".m4a",".ogg",".flac",".webm"}: return "🎵"
    if s == ".tex":       return "📐"
    if s == ".vtt":       return "💬"
    if s == ".csv":       return "📋"
    return "📄"


def index_ready() -> bool:
    return FAISS_INDEX_FILE.exists() and FAISS_METADATA_FILE.exists()


# ── Session state init ────────────────────────────────────────────────────────

def _init_state():
    if "uploaded_files_meta" not in st.session_state:
        st.session_state.uploaded_files_meta = {}   # filename -> {path, size, suffix}
    if "pipeline_status" not in st.session_state:
        st.session_state.pipeline_status = None     # PipelineStatus object
    if "pipeline_thread" not in st.session_state:
        st.session_state.pipeline_thread = None
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content":
             "👋 Bonjour ! Je suis votre assistant documentaire propulsé par **Mistral**.\n\n"
             "Commencez par uploader vos documents dans l'onglet **📂 Sources**, "
             "lancez le pipeline dans **⚙️ Pipeline**, puis revenez ici pour discuter !"}
        ]
    if "rag_model" not in st.session_state:
        st.session_state.rag_model = DEFAULT_MODEL
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = True   # dark par défaut

_init_state()


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    # ── Logo ────────────────────────────────────────────────────────────────
    dark = st.session_state.dark_mode
    _inject_theme_css(dark)

    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 .5rem;">
        <div style="font-size:2.8rem">🧠</div>
        <div style="font-size:1.15rem; font-weight:800; 
             background:linear-gradient(90deg,#6c63ff,#00d4aa);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            RAG Web App
        </div>
        <div style="color:#8b92a5; font-size:.8rem; margin-top:.2rem;">
            Mistral · FAISS · Docling
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Toggle thème ─────────────────────────────────────────────────────────
    theme_label = "☀️ Mode Clair" if dark else "🌙 Mode Sombre"
    if st.button(theme_label, use_container_width=True):
        st.session_state.dark_mode = not dark
        st.rerun()

    st.divider()

    # Statut de l'index
    if index_ready():
        st.markdown('<span class="badge badge-green">✅ Index FAISS prêt</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-yellow">⚠️ Index non construit</span>', unsafe_allow_html=True)

    n_files = len(st.session_state.uploaded_files_meta)
    st.caption(f"📂 {n_files} fichier(s) chargé(s)")

    st.divider()
    st.markdown("**⚙️ Modèle LLM**")
    model_labels = list(AVAILABLE_MODELS.keys())
    sel_label = st.selectbox(
        "Modèle",
        model_labels,
        index=model_labels.index(
            next((k for k, v in AVAILABLE_MODELS.items() if v == st.session_state.rag_model), model_labels[0])
        ),
        label_visibility="collapsed",
    )
    st.session_state.rag_model = AVAILABLE_MODELS[sel_label]
    st.caption(f"📡 `{st.session_state.rag_model}`")

    st.divider()
    if st.button("🗑️ Effacer la conversation", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content":
             "👋 Conversation effacée. Comment puis-je vous aider ?"}
        ]
        st.rerun()

    if st.button("🔄 Réinitialiser tout", use_container_width=True, type="secondary"):
        st.session_state.uploaded_files_meta = {}
        st.session_state.pipeline_status = None
        st.session_state.pipeline_thread = None
        st.rerun()

    st.divider()
    st.caption("🔑 API Mistral : " + ("✅ configurée" if MISTRAL_API_KEY else "❌ manquante"))


# ── Onglets principaux ────────────────────────────────────────────────────────

tab_sources, tab_pipeline, tab_chat = st.tabs([
    "📂  Sources",
    "⚙️  Pipeline",
    "💬  Chat",
])


# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 1 — SOURCES
# ══════════════════════════════════════════════════════════════════════════════

with tab_sources:
    st.markdown("""
    <div class="hero-header">
      <h1>📂 Gestion des Sources</h1>
      <p>Uploadez vos documents, prévisualisez-les, et préparez le pipeline RAG.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Zone d'upload ────────────────────────────────────────────────────────
    accepted_types = [
        "pdf", "docx", "pptx", "xlsx",
        "html", "htm", "csv", "tex", "vtt",
        "png", "jpg", "jpeg", "tiff", "tif", "bmp", "webp",
        "wav", "mp3", "m4a", "ogg", "flac", "webm",
    ]

    uploaded = st.file_uploader(
        "Glissez-déposez vos fichiers ici",
        type=accepted_types,
        accept_multiple_files=True,
        key="file_uploader",
        help="PDF, DOCX, PPTX, XLSX, HTML, CSV, LaTeX, images (PNG/TIFF/JPEG…), audio (WAV/MP3), WebVTT…",
        label_visibility="collapsed",
    )

    if uploaded:
        INPUTS_DIR.mkdir(parents=True, exist_ok=True)
        new_count = 0
        for uf in uploaded:
            dest = INPUTS_DIR / uf.name
            if uf.name not in st.session_state.uploaded_files_meta:
                dest.write_bytes(uf.getbuffer())
                st.session_state.uploaded_files_meta[uf.name] = {
                    "path": dest,
                    "size": uf.size,
                    "suffix": Path(uf.name).suffix.lower(),
                }
                new_count += 1
        if new_count:
            st.success(f"✅ {new_count} nouveau(x) fichier(s) ajouté(s)")
            st.rerun()

    st.markdown("---")

    # ── Liste des fichiers ───────────────────────────────────────────────────
    meta = st.session_state.uploaded_files_meta

    if not meta:
        st.markdown("""
        <div class="rag-card" style="text-align:center; padding:3rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">📭</div>
            <div style="color:#8b92a5;">Aucun fichier uploadé. Utilisez la zone ci-dessus.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        col_list, col_preview = st.columns([1, 1], gap="large")

        with col_list:
            st.markdown(f"### 📋 Fichiers chargés ({len(meta)})")

            to_delete = []
            selected_file = st.session_state.get("preview_file")

            for fname, fmeta in meta.items():
                icon = file_icon(fmeta["suffix"])
                size_str = human_size(fmeta["size"])
                is_selected = fname == selected_file

                btn_cols = st.columns([4, 1, 1])
                with btn_cols[0]:
                    st.markdown(
                        f"""<div class="file-item" style="{'border-color:#6c63ff' if is_selected else ''}">
                        <span class="file-icon">{icon}</span>
                        <span class="file-name">{fname}</span>
                        <span class="file-size">{size_str}</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with btn_cols[1]:
                    if st.button("👁", key=f"prev_{fname}", help="Prévisualiser"):
                        st.session_state.preview_file = fname
                        st.rerun()
                with btn_cols[2]:
                    if st.button("🗑", key=f"del_{fname}", help="Supprimer"):
                        to_delete.append(fname)

            if to_delete:
                for fname in to_delete:
                    fmeta = meta.pop(fname, None)
                    if fmeta and fmeta["path"].exists():
                        fmeta["path"].unlink()
                    if st.session_state.get("preview_file") == fname:
                        st.session_state.preview_file = None
                st.rerun()

            st.markdown("---")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🗑️ Tout supprimer", use_container_width=True, type="secondary"):
                    for fmeta in meta.values():
                        if fmeta["path"].exists():
                            fmeta["path"].unlink()
                    st.session_state.uploaded_files_meta = {}
                    st.session_state.preview_file = None
                    st.rerun()
            with col_b:
                # Bouton raccourci vers pipeline
                if st.button("⚙️ Lancer le pipeline →", use_container_width=True, type="primary"):
                    st.session_state._goto_pipeline = True
                    st.rerun()

        with col_preview:
            st.markdown("### 🔍 Prévisualisation")
            pfile = st.session_state.get("preview_file")

            if pfile and pfile in meta:
                fmeta = meta[pfile]
                suffix = fmeta["suffix"]
                fpath: Path = fmeta["path"]

                st.markdown(f"**{pfile}** — {human_size(fmeta['size'])}")

                # ── Prévisualisation selon le type ─────────────────────────
                if suffix in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}:
                    st.image(str(fpath), use_container_width=True)

                elif suffix == ".pdf":
                    b64 = base64.b64encode(fpath.read_bytes()).decode()
                    st.markdown(
                        f'<div class="preview-box"><iframe src="data:application/pdf;base64,{b64}" '
                        f'width="100%" height="520px" style="border:none;"></iframe></div>',
                        unsafe_allow_html=True,
                    )

                elif suffix in {".html", ".htm"}:
                    content = fpath.read_text(encoding="utf-8", errors="replace")
                    st.components.v1.html(content, height=400, scrolling=True)

                elif suffix in {".wav", ".mp3", ".m4a", ".ogg", ".flac"}:
                    st.audio(str(fpath))

                elif suffix in {".csv"}:
                    try:
                        import pandas as pd
                        df = pd.read_csv(fpath, nrows=100)
                        st.dataframe(df, use_container_width=True, height=350)
                    except Exception as e:
                        st.warning(f"Impossible de lire le CSV : {e}")

                elif suffix in {".xlsx"}:
                    try:
                        import pandas as pd
                        df = pd.read_excel(fpath, nrows=100)
                        st.dataframe(df, use_container_width=True, height=350)
                    except Exception as e:
                        st.warning(f"Impossible de lire le fichier Excel : {e}")

                elif suffix in {".docx"}:
                    try:
                        from docx import Document
                        doc = Document(fpath)
                        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                        st.text_area("Contenu DOCX", text[:3000], height=350, disabled=True)
                    except Exception:
                        st.info("⚠️ Prévisualisation DOCX non disponible.")

                elif suffix in {".pptx"}:
                    try:
                        from pptx import Presentation
                        prs = Presentation(fpath)
                        slides_text = []
                        for i, slide in enumerate(prs.slides[:10]):
                            parts = [f"── Slide {i+1} ──"]
                            for shape in slide.shapes:
                                if hasattr(shape, "text") and shape.text.strip():
                                    parts.append(shape.text.strip())
                            slides_text.append("\n".join(parts))
                        st.text_area("Aperçu PPTX (10 premières diapositives)",
                                     "\n\n".join(slides_text), height=350, disabled=True)
                    except Exception:
                        st.info("⚠️ Prévisualisation PPTX non disponible.")

                elif suffix in {".tex", ".vtt", ".webm"}:
                    text = fpath.read_text(encoding="utf-8", errors="replace")
                    st.text_area("Contenu texte", text[:3000], height=350, disabled=True)

                else:
                    st.info(f"Prévisualisation non disponible pour `{suffix}`.")
            else:
                st.markdown("""
                <div class="rag-card" style="text-align:center; padding:3rem;">
                    <div style="font-size:2.5rem">👈</div>
                    <div style="color:#8b92a5; margin-top:.5rem;">
                        Cliquez sur 👁 pour prévisualiser un fichier.
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 2 — PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

with tab_pipeline:
    st.markdown("""
    <div class="hero-header">
      <h1>⚙️ Pipeline RAG</h1>
      <p>Extraction → Chunking → Embeddings → Indexation FAISS</p>
    </div>
    """, unsafe_allow_html=True)

    from pipeline_runner import PipelineStatus, run_pipeline_async

    # État courant du pipeline
    ps: PipelineStatus | None = st.session_state.pipeline_status
    snap = ps.snapshot() if ps else None

    # ── Panneau de contrôle ──────────────────────────────────────────────────
    ctrl_col, info_col = st.columns([1, 1], gap="large")

    with ctrl_col:
        st.markdown('<div class="rag-card">', unsafe_allow_html=True)
        st.markdown("#### 🎛️ Paramètres du pipeline")

        n_files = len(st.session_state.uploaded_files_meta)
        if n_files == 0:
            st.warning("⚠️ Aucun fichier chargé. Allez d'abord dans **📂 Sources**.")

        use_mistral_emb = st.checkbox(
            "🌐 Utiliser Mistral pour les embeddings",
            value=False,
            help="Génère des embeddings plus puissants via l'API Mistral (mistral-embed). "
                 "Consomme des crédits API. Par défaut : SBERT local (gratuit, rapide).",
            disabled=not MISTRAL_API_KEY,
        )

        is_running = snap and snap["running"]
        is_done = snap and snap["done"]
        has_error = snap and snap["error"]

        btn_label = "🔄 Relancer le pipeline" if is_done else "🚀 Lancer le pipeline"

        if st.button(
            btn_label,
            disabled=(n_files == 0 or bool(is_running)),
            type="primary",
            use_container_width=True,
        ):
            # Créer l'objet de statut et lancer le thread
            new_ps = PipelineStatus()
            st.session_state.pipeline_status = new_ps
            file_paths = [m["path"] for m in st.session_state.uploaded_files_meta.values()]
            t = run_pipeline_async(file_paths, new_ps, use_mistral_embed=use_mistral_emb)
            st.session_state.pipeline_thread = t
            time.sleep(0.3)
            st.rerun()

        if is_running:
            st.markdown('<span class="badge badge-blue">⏳ Pipeline en cours…</span>', unsafe_allow_html=True)
        elif is_done:
            st.markdown('<span class="badge badge-green">✅ Pipeline terminé</span>', unsafe_allow_html=True)
        elif has_error:
            st.markdown('<span class="badge badge-red">❌ Erreur</span>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Étapes visuelles ─────────────────────────────────────────────────
        st.markdown("#### 📋 Étapes")

        steps_info = [
            ("1", "Extraction", "Docling + Whisper → Markdown",   "📄"),
            ("2", "Chunking",   "Découpage récursif + chevauchement", "✂️"),
            ("3", "Embeddings", "SBERT (+ Mistral optionnel) → vecteurs", "🧠"),
            ("4", "Indexation", "FAISS IndexFlatIP → recherche cosine", "🗄️"),
        ]

        current_step = snap["current_step"] if snap else 0

        for num, label, desc, icon in steps_info:
            n = int(num)
            if snap and snap["done"] or (snap and current_step > n):
                css = "done"
                indicator = "✅"
            elif snap and current_step == n and snap["running"]:
                css = "active"
                indicator = "⏳"
            else:
                css = "pending"
                indicator = num

            st.markdown(
                f"""<div class="step-row {css}">
                <div class="step-num">{indicator}</div>
                <div style="flex:1">
                    <div class="step-label">{icon} {label}</div>
                    <div class="step-desc">{desc}</div>
                </div>
                </div>""",
                unsafe_allow_html=True,
            )

    with info_col:
        st.markdown('<div class="rag-card">', unsafe_allow_html=True)
        st.markdown("#### 📊 Progression")

        if snap:
            if snap["running"]:
                # Barre de progression globale
                overall = (snap["current_step"] - 1) / snap["total_steps"] + \
                          (snap["step_progress"] / max(snap["step_total"], 1)) / snap["total_steps"]
                st.progress(min(overall, 0.99), text=f"Étape {snap['current_step']}/{snap['total_steps']}")
                st.caption(f"💬 {snap['step_message']}")
                # Auto-refresh pendant l'exécution
                time.sleep(1.5)
                st.rerun()

            elif snap["done"]:
                st.progress(1.0, text="✅ Terminé !")
                st.success(f"🎉 Index construit — **{snap['total_vectors']} vecteurs** indexés")
                st.caption("Vous pouvez maintenant utiliser l'onglet **💬 Chat**.")

            elif snap["error"]:
                st.error(snap["error"])
                st.progress(0.0)
        else:
            st.progress(0.0, text="En attente…")
            st.caption("Cliquez sur **Lancer le pipeline** pour démarrer.")

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Log terminal ─────────────────────────────────────────────────────
        if snap and snap["logs"]:
            st.markdown("#### 🖥️ Journal d'exécution")
            log_text = "\n".join(snap["logs"][-80:])  # dernières 80 lignes
            st.markdown(f'<div class="log-box">{log_text}</div>', unsafe_allow_html=True)

    # ── Résumé post-pipeline ─────────────────────────────────────────────────
    if snap and snap["done"]:
        st.markdown("---")
        st.markdown("#### 📈 Résultats du pipeline")
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric("📂 Fichiers traités", len(st.session_state.uploaded_files_meta))
        with m_col2:
            st.metric("🗄️ Vecteurs indexés", snap["total_vectors"])
        with m_col3:
            st.metric("📡 Modèle d'embedding", "SBERT" + (" + Mistral" if use_mistral_emb else ""))


# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 3 — CHAT
# ══════════════════════════════════════════════════════════════════════════════

with tab_chat:
    st.markdown("""
    <div class="hero-header">
      <h1>💬 Assistant RAG</h1>
      <p>Posez vos questions sur les documents indexés. Les réponses citent leurs sources.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Vérification de l'index ──────────────────────────────────────────────
    if not index_ready():
        st.info(
            "💡 **L'index FAISS n'est pas encore construit.**\n\n"
            "Pour l'utiliser :\n"
            "1. Uploadez vos documents dans **📂 Sources**\n"
            "2. Lancez le traitement dans **⚙️ Pipeline**\n"
            "3. Revenez ici pour discuter !\n\n"
            "_Le chat fonctionne également sans index (mode conversationnel)._"
        )

    # ── Fonctions LLM + RAG ──────────────────────────────────────────────────
    def get_rag_context(question: str, top_k: int = 4) -> tuple[str, list[str]]:
        """Recherche dans l'index FAISS et retourne (contexte_texte, sources)."""
        if not index_ready():
            return "", []
        try:
            from src.step_4_store.vector_store import search
            results = search(question, top_k=top_k)
            if not results:
                return "", []

            texte = ""
            sources = []
            for r in results:
                texte += (
                    f"---\nDocument : {r['metadata']['source']}\n"
                    f"Extrait : {r['text']}\n"
                )
                src = r["metadata"]["source"].split("/")[-1]
                if src not in sources:
                    sources.append(src)
            return texte, sources
        except Exception as e:
            logger.error("Erreur RAG : %s", e)
            return "", []

    def build_messages(history: list[dict], question: str, context: str) -> list:
        """Construit les messages formatés pour l'API Mistral."""
        from mistralai.models import UserMessage, AssistantMessage, SystemMessage

        system_prompt = """\
### RÔLE :
Vous êtes un assistant documentaire intelligent et bienveillant.
Vous répondez uniquement à partir des documents fournis par l'utilisateur.

### COMPORTEMENT :
- Répondez en français, de façon claire, structurée et précise.
- Citez toujours vos sources (noms de fichiers) si disponibles.
- Si l'information n'est pas dans les documents : dites-le clairement, ne l'inventez pas.
- Utilisez des listes et titres Markdown pour les réponses longues.

### INTERDICTIONS :
- Ne jamais inventer de faits.
- Ne jamais répondre sur des sujets non couverts par les documents.
"""

        formatted = [SystemMessage(content=system_prompt)]

        recent = history[-8:] if len(history) > 8 else history
        for msg in recent[:-1]:  # tous sauf le dernier (question courante)
            if msg["role"] == "user":
                formatted.append(UserMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                formatted.append(AssistantMessage(content=msg["content"]))

        # Enrichir la question avec le contexte RAG si disponible
        if context:
            enriched = (
                f"### DOCUMENTS PERTINENTS :\n{context}\n\n"
                f"### QUESTION :\n{question}"
            )
        else:
            enriched = question

        formatted.append(UserMessage(content=enriched))
        return formatted

    def call_llm(messages: list, model: str) -> str:
        """Appelle l'API Mistral et retourne la réponse."""
        if not MISTRAL_API_KEY:
            return "❌ Clé API Mistral non configurée. Veuillez définir `MISTRAL_API_KEY` dans le fichier `.env`."
        try:
            from mistralai import Mistral
            client = Mistral(api_key=MISTRAL_API_KEY)
            resp = client.chat.complete(model=model, messages=messages, **GENERATION_PARAMS)
            if resp.choices:
                return resp.choices[0].message.content
            return "Je suis désolé, je n'ai pas pu générer de réponse."
        except Exception as e:
            logger.error("Erreur LLM : %s", e)
            return f"❌ Erreur lors de l'appel à Mistral : {e}"

    # ── Affichage de l'historique ────────────────────────────────────────────
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── Saisie utilisateur ───────────────────────────────────────────────────
    if prompt := st.chat_input("Posez votre question sur vos documents…"):
        # Ajouter le message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Recherche RAG
        with st.spinner("🔍 Recherche dans les documents…"):
            ctx_text, sources = get_rag_context(prompt)

        # Construire les messages
        prompt_messages = build_messages(st.session_state.messages, prompt, ctx_text)

        # Générer la réponse
        with st.chat_message("assistant"):
            with st.spinner("🤔 Génération de la réponse…"):
                answer = call_llm(prompt_messages, st.session_state.rag_model)
            st.markdown(answer)

            if sources:
                sources_md = ", ".join([f"`{s}`" for s in sources])
                st.caption(f"📚 **Sources utilisées :** {sources_md}")
                answer += f"\n\n*📚 Sources : {', '.join(sources)}*"
            elif not ctx_text and index_ready():
                st.caption("ℹ️ Aucun document pertinent trouvé pour cette question.")

        st.session_state.messages.append({"role": "assistant", "content": answer})
