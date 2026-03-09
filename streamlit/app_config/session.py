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
                    "👋 Bonjour ! Je suis votre assistant documentaire propulsé par **Mistral**.\n\n"
                    "Commencez par uploader vos documents dans l'onglet **📂 Sources**, "
                    "lancez le pipeline dans **⚙️ Pipeline**, puis revenez ici pour discuter !"
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
