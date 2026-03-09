"""
Fonctions utilitaires de l'interface.

Contient les helpers partagés (formatage de taille, icônes, vérifications).
"""

from __future__ import annotations

from app_config.settings import FAISS_INDEX_FILE, FAISS_METADATA_FILE


def human_size(n_bytes: int) -> str:
    """Formate un nombre d'octets en taille lisible."""
    for unit in ("o", "Ko", "Mo", "Go"):
        if n_bytes < 1024:
            return f"{n_bytes:.0f} {unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} To"


def file_icon(suffix: str) -> str:
    """Retourne un emoji représentant le type de fichier."""
    s = suffix.lower()
    if s == ".pdf":       return "📕"
    if s == ".docx":      return "📘"
    if s == ".pptx":      return "📊"
    if s == ".xlsx":      return "📗"
    if s in {".html", ".htm"}: return "🌐"
    if s in {".png", ".jpg", ".jpeg", ".webp", ".tiff", ".tif", ".bmp"}: return "🖼️"
    if s in {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm"}: return "🎵"
    if s == ".tex":       return "📐"
    if s == ".vtt":       return "💬"
    if s == ".csv":       return "📋"
    return "📄"


def index_ready() -> bool:
    """Vérifie si l'index FAISS et les métadonnées existent."""
    return FAISS_INDEX_FILE.exists() and FAISS_METADATA_FILE.exists()


def complete_reset() -> None:
    """Réinitialise complètement l'application (supprime les fichiers uploadés, index, meta, et session_state)."""
    import shutil
    from app_config.settings import INPUTS_DIR, MARKDOWN_DIR, CHUNKS_DIR, VECTORSTORE_DIR
    import streamlit as st

    # 1. Supprimer les dossiers de données
    for d in [INPUTS_DIR, MARKDOWN_DIR, CHUNKS_DIR, VECTORSTORE_DIR]:
        if d.exists() and d.is_dir():
            shutil.rmtree(d, ignore_errors=True)
            
    # 2. Réinitialiser la session state
    st.session_state.uploaded_files_meta = {}
    st.session_state.pipeline_status = None
    st.session_state.pipeline_thread = None
    st.session_state.files_validated = False
    st.session_state.edit_mode = False
    st.session_state._popup_dismissed = False
    st.session_state.file_uploader_key = st.session_state.get("file_uploader_key", 0) + 1
    
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "👋 Bonjour, je suis l'assistant virtuel de la mairie de Trifouillis-sur-Loire. "
                "Comment puis-je vous aider aujourd'hui ?\n\n"
                "_(Note de l'administration : N'oubliez pas d'insérer les documents municipaux "
                "dans l'onglet **📂 Sources** et de lancer le **⚙️ Pipeline** si besoin.)_"
            ),
        }
    ]
