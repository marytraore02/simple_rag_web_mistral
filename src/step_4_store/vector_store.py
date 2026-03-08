"""
Étape 4 — Stockage vectoriel FAISS et recherche sémantique.

Usage depuis le pipeline :
    from src.step_4_store.vector_store import run_store, search
    run_store(embeddings, chunks, progress_callback=cb)
    results = search("Ma question", top_k=5)
"""

from __future__ import annotations

import json
import sys
import logging
from pathlib import Path
from typing import Callable, List, Optional

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from config import (
    FAISS_INDEX_FILE, FAISS_METADATA_FILE, FAISS_TOP_K,
    EMBEDDINGS_OUTPUT_FILE, CHUNKS_OUTPUT_FILE,
    SBERT_MODEL_NAME,
    LOG_LEVEL, LOG_FORMAT, LOG_DATEFMT,
)

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, int, str], None]


# ── Construction de l'index ──────────────────────────────────────────────────


def build_faiss_index(embeddings: np.ndarray):
    """
    Construit un index FAISS à partir d'embeddings.
    Utilise IndexFlatIP avec normalisation L2 (= cosine similarity).
    """
    import faiss

    embeddings_normalized = embeddings.copy().astype("float32")
    faiss.normalize_L2(embeddings_normalized)

    dimension = embeddings_normalized.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings_normalized)

    logger.info("   Index FAISS : %d vecteurs, dim=%d", index.ntotal, dimension)
    return index


def save_index(index, chunks: list[dict],
               index_file: Path | None = None,
               metadata_file: Path | None = None) -> None:
    """Sauvegarde l'index FAISS et les métadonnées."""
    import faiss

    index_file = index_file or FAISS_INDEX_FILE
    metadata_file = metadata_file or FAISS_METADATA_FILE

    index_file.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_file))
    logger.info("   💾 Index FAISS → %s", index_file)

    metadata = [{"text": c["text"], "metadata": c["metadata"]} for c in chunks]
    metadata_file.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("   💾 Métadonnées → %s", metadata_file)


def load_index(index_file: Path | None = None,
               metadata_file: Path | None = None) -> tuple:
    """Charge l'index FAISS et les métadonnées."""
    import faiss

    index_file = index_file or FAISS_INDEX_FILE
    metadata_file = metadata_file or FAISS_METADATA_FILE

    if not index_file.exists() or not metadata_file.exists():
        logger.error("Index FAISS ou métadonnées introuvables.")
        return None, None

    index = faiss.read_index(str(index_file))
    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    logger.info("   Index chargé : %d vecteurs", index.ntotal)
    return index, metadata


# ── Recherche sémantique ─────────────────────────────────────────────────────


def search(
    query: str,
    top_k: int = FAISS_TOP_K,
    index_file: Path | None = None,
    metadata_file: Path | None = None,
    model_name: str = SBERT_MODEL_NAME,
) -> list[dict]:
    """
    Recherche les chunks les plus similaires à une requête.

    Retourne :
        Liste de dicts : {rank, score, text, metadata}
    """
    import faiss
    from sentence_transformers import SentenceTransformer

    index, metadata = load_index(index_file, metadata_file)
    if index is None:
        return []

    model = SentenceTransformer(model_name)
    query_embedding = model.encode([query]).astype("float32")
    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, top_k)

    results = []
    for rank, (idx, score) in enumerate(zip(indices[0], scores[0])):
        if idx < 0 or idx >= len(metadata):
            continue
        results.append({
            "rank": rank + 1,
            "score": float(score),
            "text": metadata[idx]["text"],
            "metadata": metadata[idx]["metadata"],
        })

    return results


# ── Point d'entrée ───────────────────────────────────────────────────────────


def run_store(
    embeddings: np.ndarray | None = None,
    chunks: list[dict] | None = None,
    embedding_type: str = "sbert",
    progress_callback: ProgressCallback | None = None,
) -> dict:
    """
    Point d'entrée de l'étape 4 : construction du vector store FAISS.

    Retourne :
        {"index": faiss.Index | None, "total_vectors": int}
    """
    logger.info("=" * 65)
    logger.info("🗄️  ÉTAPE 4 — STOCKAGE VECTORIEL (FAISS)")
    logger.info("=" * 65)

    if progress_callback:
        progress_callback(0, 3, "⏳ Chargement des embeddings…")

    if embeddings is None:
        if not EMBEDDINGS_OUTPUT_FILE.exists():
            logger.error("Fichier d'embeddings introuvable : %s", EMBEDDINGS_OUTPUT_FILE)
            return {"index": None, "total_vectors": 0}

        data = np.load(str(EMBEDDINGS_OUTPUT_FILE))
        if embedding_type in data:
            embeddings = data[embedding_type]
        else:
            logger.error("Type '%s' introuvable. Disponibles : %s", embedding_type, list(data.keys()))
            return {"index": None, "total_vectors": 0}

    if chunks is None:
        if not CHUNKS_OUTPUT_FILE.exists():
            logger.error("Fichier de chunks introuvable : %s", CHUNKS_OUTPUT_FILE)
            return {"index": None, "total_vectors": 0}
        with open(CHUNKS_OUTPUT_FILE, "r", encoding="utf-8") as f:
            chunks = json.load(f).get("chunks", [])

    if len(embeddings) != len(chunks):
        logger.error("Incohérence : %d embeddings ≠ %d chunks", len(embeddings), len(chunks))
        return {"index": None, "total_vectors": 0}

    if progress_callback:
        progress_callback(1, 3, "🔨 Construction de l'index FAISS…")

    index = build_faiss_index(embeddings)

    if progress_callback:
        progress_callback(2, 3, "💾 Sauvegarde de l'index…")

    save_index(index, chunks)

    if progress_callback:
        progress_callback(3, 3, f"✅ Index FAISS prêt — {index.ntotal} vecteurs")

    logger.info("✅ Étape 4 terminée ! Index FAISS prêt.")
    return {"index": index, "total_vectors": index.ntotal}


def index_exists(
    index_file: Path | None = None,
    metadata_file: Path | None = None,
) -> bool:
    """Vérifie si l'index FAISS existe."""
    index_file = index_file or FAISS_INDEX_FILE
    metadata_file = metadata_file or FAISS_METADATA_FILE
    return index_file.exists() and metadata_file.exists()


# ── Exécution autonome ──────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, datefmt=LOG_DATEFMT)
    run_store()
