"""
Paramètres de l'application Streamlit.

Réimporte les constantes depuis le fichier config.py racine
et définit les chemins internes au module Streamlit.
"""

from __future__ import annotations

import sys
from pathlib import Path

# ── Chemins du module Streamlit ──────────────────────────────────────────────
APP_DIR = Path(__file__).resolve().parent.parent   # streamlit/
ROOT_DIR = APP_DIR.parent                           # simple_rag_web_mistral/

# Rendre le dossier racine importable
sys.path.insert(0, str(ROOT_DIR))

# ── Réimport des constantes depuis config.py ─────────────────────────────────
from config import (  # noqa: E402
    INPUTS_DIR,
    MARKDOWN_DIR,
    CHUNKS_DIR,
    VECTORSTORE_DIR,
    FAISS_INDEX_FILE,
    FAISS_METADATA_FILE,
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
    GENERATION_PARAMS,
    SUPPORTED_EXTENSIONS,
    DOCLING_EXTENSIONS,
    AUDIO_EXTENSIONS,
    MISTRAL_API_KEY,
    SBERT_MODEL_NAME,
    CHUNKS_OUTPUT_FILE,
    EMBEDDINGS_OUTPUT_FILE,
)
