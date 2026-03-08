"""
Module de gestion du pipeline RAG.

Orchestre les 4 étapes dans un thread séparé et expose
l'état du pipeline via un objet partagé thread-safe.
"""

import logging
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)


@dataclass
class PipelineStatus:
    """État partagé du pipeline (thread-safe via lock)."""

    running: bool = False
    done: bool = False
    error: str | None = None

    # Étape globale (1-4) et avancement
    current_step: int = 0          # 0 = pas démarré
    total_steps: int = 4

    # Détail de l'étape courante
    step_progress: int = 0
    step_total: int = 100
    step_message: str = ""

    # Log textuel riche
    logs: list[str] = field(default_factory=list)

    # Résultat final
    total_vectors: int = 0

    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def update(self, **kwargs) -> None:
        with self._lock:
            for k, v in kwargs.items():
                if k != "_lock":
                    setattr(self, k, v)

    def add_log(self, msg: str) -> None:
        with self._lock:
            self.logs.append(msg)
            logger.info(msg)

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "running": self.running,
                "done": self.done,
                "error": self.error,
                "current_step": self.current_step,
                "total_steps": self.total_steps,
                "step_progress": self.step_progress,
                "step_total": self.step_total,
                "step_message": self.step_message,
                "logs": list(self.logs),
                "total_vectors": self.total_vectors,
            }


def run_pipeline_async(
    file_paths: list[Path],
    status: PipelineStatus,
    use_mistral_embed: bool = False,
) -> threading.Thread:
    """
    Lance le pipeline RAG dans un thread démon et retourne le thread.

    Paramètres :
        file_paths         : fichiers à indexer
        status             : objet PipelineStatus partagé
        use_mistral_embed  : utiliser l'API Mistral pour les embeddings
    """

    def _run():
        import sys
        from pathlib import Path as P

        sys.path.insert(0, str(P(__file__).resolve().parents[1]))

        try:
            status.update(running=True, done=False, error=None, logs=[], current_step=0)

            # ── Étape 1 : Extraction ──────────────────────────────────────
            status.update(current_step=1, step_message="Extraction des documents…")
            status.add_log("🚀 Démarrage du pipeline RAG")
            status.add_log(f"   {len(file_paths)} fichier(s) à traiter")

            from src.step_1_extract.extractor import run_extraction

            def cb1(cur, tot, msg):
                status.update(step_progress=cur, step_total=max(tot, 1), step_message=msg)
                status.add_log(f"   [Extraction] {msg}")

            result1 = run_extraction(file_paths=file_paths, progress_callback=cb1)
            status.add_log(
                f"✅ Étape 1 — {result1['success_count']}/{result1['total_files']} fichiers extraits"
            )

            if result1["success_count"] == 0:
                raise RuntimeError("Aucun document n'a pu être extrait.")

            # ── Étape 2 : Chunking ────────────────────────────────────────
            status.update(current_step=2, step_message="Découpage en chunks…")
            status.add_log("✂️  Étape 2 — Chunking…")

            from src.step_2_chunk.chunker import run_chunking

            def cb2(cur, tot, msg):
                status.update(step_progress=cur, step_total=max(tot, 1), step_message=msg)
                status.add_log(f"   [Chunking] {msg}")

            chunks = run_chunking(progress_callback=cb2)
            status.add_log(f"✅ Étape 2 — {len(chunks)} chunks générés")

            # ── Étape 3 : Embeddings ──────────────────────────────────────
            status.update(current_step=3, step_message="Génération des embeddings…")
            status.add_log("🧠 Étape 3 — Embeddings SBERT…")

            from src.step_3_embed.embedder import run_embedding

            def cb3(cur, tot, msg):
                status.update(step_progress=cur, step_total=max(tot, 1), step_message=msg)
                status.add_log(f"   [Embedding] {msg}")

            emb_result = run_embedding(
                chunks=chunks,
                use_sbert=True,
                use_mistral=use_mistral_embed,
                visualize=False,
                progress_callback=cb3,
            )
            status.add_log("✅ Étape 3 — Embeddings générés")

            # ── Étape 4 : Vector Store ────────────────────────────────────
            status.update(current_step=4, step_message="Construction de l'index FAISS…")
            status.add_log("🗄️  Étape 4 — Indexation FAISS…")

            from src.step_4_store.vector_store import run_store

            def cb4(cur, tot, msg):
                status.update(step_progress=cur, step_total=max(tot, 1), step_message=msg)
                status.add_log(f"   [FAISS] {msg}")

            store_result = run_store(
                embeddings=emb_result.get("sbert_embeddings"),
                chunks=emb_result.get("chunks"),
                progress_callback=cb4,
            )

            total_vec = store_result.get("total_vectors", 0)
            status.add_log(f"✅ Étape 4 — {total_vec} vecteurs indexés")
            status.add_log("🎉 Pipeline RAG terminé avec succès !")
            status.update(
                running=False,
                done=True,
                total_vectors=total_vec,
                current_step=4,
                step_message="Pipeline terminé !",
            )

        except Exception as e:
            err = f"❌ Erreur pipeline : {e}"
            status.add_log(err)
            status.update(running=False, done=False, error=err)
            logger.error(err, exc_info=True)

    t = threading.Thread(target=_run, daemon=True, name="rag-pipeline")
    t.start()
    return t
