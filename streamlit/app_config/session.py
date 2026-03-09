"""
Initialisation du session state Streamlit.

Centralise toutes les clés du session_state
pour garantir qu'elles existent dès le démarrage.
"""

from __future__ import annotations

import streamlit as st

from app_config.settings import DEFAULT_MODEL


def init_session_state() -> None:
    """Initialise toutes les clés du session state si elles n'existent pas."""
    defaults = {
        "uploaded_files_meta": {},
        "pipeline_status": None,
        "pipeline_thread": None,
        "messages": [
            {
                "role": "assistant",
                "content": (
                    "👋 Bonjour, je suis l'assistant virtuel de la mairie de Trifouillis-sur-Loire. "
                    "Comment puis-je vous aider aujourd'hui ?\n\n"
                    "_(Note de l'administration : N'oubliez pas d'insérer les documents municipaux "
                    "dans l'onglet **📂 Sources** et de lancer le **⚙️ Pipeline** si besoin.)_"
                ),
            }
        ],
        "rag_model": DEFAULT_MODEL,
        "dark_mode": True,
        "file_uploader_key": 0,
        "files_validated": False,
        "edit_mode": False,
        "show_success_popup": False,
        "_popup_dismissed": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
