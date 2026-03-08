"""
Étape 1 — Extraction de documents sources vers Markdown.

Améliorations vs simple_rag_steps :
  - Accepte une liste de Path en entrée (fichiers uploadés)
  - Expose un progress_callback(step, total, message) pour le suivi UI
  - Gestion propre des fichiers temporaires

Usage depuis le pipeline :
    from src.step_1_extract.extractor import run_extraction
    result = run_extraction(file_paths=[...], progress_callback=cb)
"""

from __future__ import annotations

import os
import sys
import logging
from pathlib import Path
from typing import Callable, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from config import (
    INPUTS_DIR, MARKDOWN_DIR,
    DOCLING_EXTENSIONS, AUDIO_EXTENSIONS, SUPPORTED_EXTENSIONS,
    WHISPER_MODEL_SIZE, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE, WHISPER_BEAM_SIZE,
    LOG_LEVEL, LOG_FORMAT, LOG_DATEFMT,
)

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, int, str], None]


# ── Fonctions ────────────────────────────────────────────────────────────────


def discover_files(input_dir: Path) -> list[Path]:
    """Parcourt récursivement le répertoire et retourne les fichiers supportés."""
    files: list[Path] = []
    for root, _dirs, filenames in os.walk(input_dir):
        for filename in sorted(filenames):
            filepath = Path(root) / filename
            if filepath.suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(filepath)
            else:
                logger.warning("Extension non supportée, ignoré : %s", filepath.name)
    return files


def transcribe_audio(
    whisper_model,
    source_path: Path,
    output_path: Path,
    input_dir: Path,
 ) -> bool:
    """
    Transcrit un fichier audio en Markdown via Faster-Whisper.
    Retourne True si la transcription a réussi.
    """
    try:
        logger.info("🎤 Transcription : %s", source_path.name)

        segments, info = whisper_model.transcribe(
            str(source_path),
            beam_size=WHISPER_BEAM_SIZE,
            vad_filter=True,
        )

        logger.info(
            "   Langue : %s (%.1f%%) | Durée : %.1f s",
            info.language,
            info.language_probability * 100,
            info.duration,
        )

        all_segments = list(segments)
        transcription_text = " ".join([s.text.strip() for s in all_segments])

        if not transcription_text.strip():
            transcription_text = "*Aucun contenu vocal détecté dans ce fichier audio.*"

        markdown_lines = [
            f"# Transcription : {source_path.stem}",
            "",
            f"- **Fichier source** : `{source_path.name}`",
            f"- **Langue détectée** : {info.language} ({info.language_probability * 100:.1f}%)",
            f"- **Durée** : {info.duration:.1f} secondes ({info.duration / 60:.1f} minutes)",
            f"- **Modèle utilisé** : Whisper {WHISPER_MODEL_SIZE} (faster-whisper, {WHISPER_COMPUTE_TYPE})",
            f"- **Nombre de segments** : {len(all_segments)}",
            "",
            "---",
            "",
            "## Transcription complète",
            "",
            transcription_text,
            "",
            "---",
            "",
            "## Segments détaillés",
            "",
        ]

        for seg in all_segments:
            start_min, start_sec = divmod(seg.start, 60)
            end_min, end_sec = divmod(seg.end, 60)
            markdown_lines.append(
                f"- **[{int(start_min):02d}:{start_sec:05.2f} → "
                f"{int(end_min):02d}:{end_sec:05.2f}]** {seg.text.strip()}"
            )

        markdown_content = "\n".join(markdown_lines) + "\n"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown_content, encoding="utf-8")
        logger.info("  ✅ Transcription → %s", output_path.name)
        return True

    except Exception as e:
        logger.error("  ❌ Échec transcription pour %s : %s", source_path.name, e)
        return False


def convert_file(
    converter,
    source_path: Path,
    output_path: Path,
    input_dir: Path,
 ) -> bool:
    """
    Convertit un fichier document en Markdown via Docling.
    Retourne True si la conversion a réussi.
    """
    try:
        logger.info("📄 Conversion : %s", source_path.name)
        result = converter.convert(str(source_path))
        markdown_content = result.document.export_to_markdown()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown_content, encoding="utf-8")
        logger.info("  ✅ Sauvegardé → %s", output_path.name)
        return True

    except Exception as e:
        logger.error("  ❌ Échec pour %s : %s", source_path.name, e)
        return False


def run_extraction(
    file_paths: list[Path] | None = None,
    input_dir: Path | None = None,
    output_dir: Path | None = None,
    progress_callback: ProgressCallback | None = None,
) -> dict:
    """
    Point d'entrée de l'étape 1 : extraction de documents vers Markdown.

    Paramètres :
        file_paths        : liste de fichiers à traiter (prioritaire sur input_dir)
        input_dir         : répertoire source (défaut : config.INPUTS_DIR)
        output_dir        : répertoire Markdown de sortie (défaut : config.MARKDOWN_DIR)
        progress_callback : fn(current, total, message) pour le suivi UI

    Retourne :
        {"success_count": int, "fail_count": int, "total_files": int, "output_dir": str}
    """
    output_dir = output_dir or MARKDOWN_DIR

    # Résoudre la liste de fichiers
    if file_paths is not None:
        files = [Path(p) for p in file_paths if Path(p).suffix.lower() in SUPPORTED_EXTENSIONS]
        effective_input_dir = output_dir  # non utilisé pour le chemin relatif ici
    else:
        effective_input_dir = input_dir or INPUTS_DIR
        files = discover_files(effective_input_dir)

    if not files:
        logger.warning("Aucun fichier supporté trouvé")
        return {"success_count": 0, "fail_count": 0, "total_files": 0, "output_dir": str(output_dir)}

    audio_files = [f for f in files if f.suffix.lower() in AUDIO_EXTENSIONS]
    doc_files = [f for f in files if f.suffix.lower() in DOCLING_EXTENSIONS]

    logger.info("=" * 65)
    logger.info("📄 ÉTAPE 1 — EXTRACTION VERS MARKDOWN")
    logger.info("  Documents (Docling) : %d", len(doc_files))
    logger.info("  Audios (Whisper)    : %d", len(audio_files))
    logger.info("=" * 65)

    output_dir.mkdir(parents=True, exist_ok=True)
    success_count = 0
    fail_count = 0
    total = len(files)
    current = 0

    def _cb(msg: str):
        nonlocal current
        current += 1
        if progress_callback:
            progress_callback(current, total, msg)

    # ── Audio avec Faster-Whisper ──────────────────────────────────────────
    if audio_files:
        from faster_whisper import WhisperModel

        if progress_callback:
            progress_callback(current, total, f"⏳ Chargement du modèle Whisper '{WHISPER_MODEL_SIZE}'…")

        whisper_model = WhisperModel(
            WHISPER_MODEL_SIZE,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )

        for source_path in audio_files:
            output_path = output_dir / (source_path.stem + ".md")
            ok = transcribe_audio(whisper_model, source_path, output_path, output_dir)
            success_count += ok
            fail_count += not ok
            _cb(f"🎤 {'✅' if ok else '❌'} {source_path.name}")

        del whisper_model

    # ── Documents avec Docling ─────────────────────────────────────────────
    if doc_files:
        from docling.document_converter import DocumentConverter

        if progress_callback:
            progress_callback(current, total, "⏳ Initialisation de Docling…")

        converter = DocumentConverter()

        for source_path in doc_files:
            output_path = output_dir / (source_path.stem + ".md")
            ok = convert_file(converter, source_path, output_path, output_dir)
            success_count += ok
            fail_count += not ok
            _cb(f"📄 {'✅' if ok else '❌'} {source_path.name}")

    logger.info("🏁 Extraction terminée ! ✅ %d | ❌ %d", success_count, fail_count)

    return {
        "success_count": success_count,
        "fail_count": fail_count,
        "total_files": total,
        "output_dir": str(output_dir),
    }


# ── Exécution autonome ──────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, datefmt=LOG_DATEFMT)
    run_extraction()
