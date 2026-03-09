"""
Module RAG — Recherche sémantique dans l'index FAISS.

Récupère le contexte pertinent pour enrichir les réponses du LLM.
"""

from __future__ import annotations

import logging

from utils.helpers import index_ready

logger = logging.getLogger(__name__)


def get_rag_context(question: str, top_k: int = 4) -> tuple[str, list[str]]:
    """
    Recherche dans l'index FAISS et retourne le contexte + les sources.

    Paramètres :
        question : question de l'utilisateur
        top_k    : nombre de résultats à retourner

    Retourne :
        (contexte_texte, liste_de_sources)
    """
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
