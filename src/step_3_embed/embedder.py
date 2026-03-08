"""
Étape 3 — Vectorisation (embeddings) des chunks.

Usage depuis le pipeline :
    from src.step_3_embed.embedder import run_embedding
    result = run_embedding(chunks, progress_callback=cb)
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
    CHUNKS_OUTPUT_FILE, EMBEDDINGS_OUTPUT_FILE, PLOTS_DIR,
    SBERT_MODEL_NAME, MISTRAL_API_KEY, MISTRAL_EMBED_MODEL, MISTRAL_BATCH_SIZE,
    LOG_LEVEL, LOG_FORMAT, LOG_DATEFMT,
)

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, int, str], None]


# ── Fonctions d'embedding ────────────────────────────────────────────────────


def load_chunks(chunks_file: Path) -> list[dict]:
    """Charge les chunks depuis le fichier JSON."""
    with open(chunks_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("chunks", [])


def embed_with_sbert(
    texts: list[str],
    model_name: str = SBERT_MODEL_NAME,
    progress_callback: ProgressCallback | None = None,
) -> np.ndarray:
    """Génère les embeddings avec un modèle SBERT local."""
    from sentence_transformers import SentenceTransformer

    logger.info("🧠 Génération des embeddings SBERT (%s)…", model_name)

    if progress_callback:
        progress_callback(0, len(texts), f"⏳ Chargement du modèle SBERT ({model_name})…")

    model = SentenceTransformer(model_name)

    batch_size = 32
    all_embs = []
    total = len(texts)

    for i in range(0, total, batch_size):
        batch = texts[i : i + batch_size]
        embs = model.encode(batch, show_progress_bar=False)
        all_embs.extend(embs)
        if progress_callback:
            progress_callback(
                min(i + batch_size, total),
                total,
                f"🧠 SBERT : {min(i + batch_size, total)}/{total} chunks vectorisés",
            )

    embeddings = np.array(all_embs)
    logger.info("   ✅ SBERT : shape=%s", embeddings.shape)
    return embeddings


def embed_with_mistral(
    texts: list[str],
    api_key: str | None = MISTRAL_API_KEY,
    progress_callback: ProgressCallback | None = None,
) -> np.ndarray | None:
    """Génère les embeddings via l'API Mistral."""
    if not api_key:
        logger.warning("⚠️ Pas de clé API Mistral → embeddings Mistral ignorés")
        return None

    from mistralai import Mistral

    logger.info("🧠 Génération des embeddings Mistral (%s)…", MISTRAL_EMBED_MODEL)

    client = Mistral(api_key=api_key)
    all_embeddings = []
    total_batches = (len(texts) - 1) // MISTRAL_BATCH_SIZE + 1

    for i in range(0, len(texts), MISTRAL_BATCH_SIZE):
        batch = texts[i : i + MISTRAL_BATCH_SIZE]
        response = client.embeddings.create(
            model=MISTRAL_EMBED_MODEL,
            inputs=batch,
        )
        all_embeddings.extend([d.embedding for d in response.data])
        batch_num = i // MISTRAL_BATCH_SIZE + 1
        if progress_callback:
            progress_callback(
                i + len(batch),
                len(texts),
                f"🌐 Mistral API : batch {batch_num}/{total_batches}",
            )

    embeddings = np.array(all_embeddings)
    logger.info("   ✅ Mistral : shape=%s", embeddings.shape)
    return embeddings


# ── Point d'entrée ───────────────────────────────────────────────────────────


def run_embedding(
    chunks: list[dict] | None = None,
    chunks_file: Path | None = None,
    output_file: Path | None = None,
    use_mistral: bool = False,
    use_sbert: bool = True,
    visualize: bool = False,
    progress_callback: ProgressCallback | None = None,
) -> dict:
    """
    Point d'entrée de l'étape 3 : génération des embeddings.

    Paramètres :
        chunks            : liste de chunks (si None, charge depuis JSON)
        chunks_file       : chemin du fichier JSON des chunks
        output_file       : fichier .npz de sortie
        use_mistral       : génère les embeddings Mistral (coûteux)
        use_sbert         : génère les embeddings SBERT (local, gratuit)
        visualize         : génère les plots PCA
        progress_callback : fn(current, total, message)

    Retourne :
        {"sbert_embeddings", "mistral_embeddings", "chunks", "texts"}
    """
    chunks_file = chunks_file or CHUNKS_OUTPUT_FILE
    output_file = output_file or EMBEDDINGS_OUTPUT_FILE

    logger.info("=" * 65)
    logger.info("🧠 ÉTAPE 3 — VECTORISATION (EMBEDDINGS)")
    logger.info("=" * 65)

    if chunks is None:
        if not chunks_file.exists():
            logger.error("Fichier de chunks introuvable : %s", chunks_file)
            return {"sbert_embeddings": None, "mistral_embeddings": None, "chunks": [], "texts": []}
        chunks = load_chunks(chunks_file)

    texts = [c["text"] for c in chunks]
    logger.info("   %d chunks à vectoriser", len(texts))

    result = {
        "sbert_embeddings": None,
        "mistral_embeddings": None,
        "chunks": chunks,
        "texts": texts,
    }

    if use_sbert:
        result["sbert_embeddings"] = embed_with_sbert(texts, progress_callback=progress_callback)

        if visualize and result["sbert_embeddings"] is not None:
            _plot_embeddings(
                result["sbert_embeddings"],
                chunks,
                f"Embeddings SBERT ({SBERT_MODEL_NAME}) — {len(chunks)} chunks",
                PLOTS_DIR / "sbert_embeddings.png",
            )

    if use_mistral:
        result["mistral_embeddings"] = embed_with_mistral(texts, progress_callback=progress_callback)

        if visualize and result["mistral_embeddings"] is not None:
            _plot_embeddings(
                result["mistral_embeddings"],
                chunks,
                f"Embeddings Mistral ({MISTRAL_EMBED_MODEL}) — {len(chunks)} chunks",
                PLOTS_DIR / "mistral_embeddings.png",
            )

    # Sauvegarde
    save_data = {}
    if result["sbert_embeddings"] is not None:
        save_data["sbert"] = result["sbert_embeddings"]
    if result["mistral_embeddings"] is not None:
        save_data["mistral"] = result["mistral_embeddings"]

    if save_data:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(str(output_file), **save_data)
        logger.info("💾 Embeddings sauvegardés → %s", output_file)

    if progress_callback:
        progress_callback(len(texts), len(texts), f"✅ {len(texts)} vecteurs générés")

    logger.info("✅ Étape 3 terminée !")
    return result


def _plot_embeddings(embeddings: np.ndarray, chunks: list[dict], title: str, output_file: Path) -> None:
    """Réduit avec PCA et visualise les embeddings en 2D."""
    try:
        from sklearn.decomposition import PCA
        import matplotlib.pyplot as plt
        import seaborn as sns
        import pandas as pd

        pca = PCA(n_components=2)
        coords = pca.fit_transform(embeddings)
        categories = [c["metadata"]["category"] for c in chunks]

        df = pd.DataFrame({"x": coords[:, 0], "y": coords[:, 1], "category": categories})
        plt.figure(figsize=(14, 9))
        sns.scatterplot(data=df, x="x", y="y", hue="category", style="category", s=80, alpha=0.8)
        plt.title(title, fontsize=14, fontweight="bold")
        plt.tight_layout()

        output_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_file, dpi=150)
        plt.close()
        logger.info("   ✅ Plot → %s", output_file)
    except Exception as e:
        logger.warning("Plot PCA échoué : %s", e)


# ── Exécution autonome ──────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, datefmt=LOG_DATEFMT)
    run_embedding()
