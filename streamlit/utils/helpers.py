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
