"""
RAG Web App — Assistant documentaire avec Mistral.
Point d'entrée principal de l'application Streamlit.

Interface en 4 onglets :
  📂 Sources   — Upload, prévisualisation et gestion des fichiers
  ⚙️ Pipeline  — Lancement et suivi du pipeline RAG
  💬 Chat      — Assistant RAG conversationnel
  📊 Visualisation — Exploration de l'espace sémantique

Usage :
    streamlit run streamlit/app.py
"""

from __future__ import annotations

import logging
import streamlit as st

# Configuration Streamlit de base (DOIT être le premier call Streamlit)
st.set_page_config(
    page_title="RAG Assistant — Mistral",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 1. Config et init
from app_config.session import init_session_state
init_session_state()

# 2. Imports UI
from ui.sidebar import render_sidebar
from ui.pages import sources, pipeline, chat, visualization

# Logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Fonction principale de l'application."""
    
    # ── Sidebar ──────────────────────────────────────────────────────────
    render_sidebar()

    # ── Structure des Onglets ────────────────────────────────────────────
    tab_sources, tab_pipeline, tab_chat, tab_viz = st.tabs([
        "📂  Sources",
        "⚙️  Pipeline",
        "💬  Chat",
        "📊  Visualisation",
    ])

    # ── Rendu des pages ──────────────────────────────────────────────────
    sources.render(tab_sources)
    pipeline.render(tab_pipeline)
    chat.render(tab_chat)
    visualization.render(tab_viz)


if __name__ == "__main__":
    main()
