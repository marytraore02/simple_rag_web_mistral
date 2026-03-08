"""
Étape 2 — Découpage récursif avec chevauchement (chunking).

Usage depuis le pipeline :
    from src.step_2_chunk.chunker import run_chunking
    chunks = run_chunking(progress_callback=cb)
"""

import json
import sys
import logging
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from config import (
    MARKDOWN_DIR, CHUNKS_OUTPUT_FILE,
    CHUNK_SIZE, CHUNK_OVERLAP, HEADERS_TO_SPLIT_ON, SEPARATORS,
    LOG_LEVEL, LOG_FORMAT, LOG_DATEFMT,
)

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, int, str], None]


# ── Fonctions ────────────────────────────────────────────────────────────────


def load_markdown_files(input_dir: Path) -> list[dict]:
    """Charge tous les fichiers .md depuis le répertoire d'entrée."""
    documents = []

    for md_file in sorted(input_dir.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8").strip()

        if len(content) < 10:
            logger.warning("Fichier trop court, ignoré : %s", md_file.name)
            continue

        relative = md_file.relative_to(input_dir)
        category = relative.parts[0] if len(relative.parts) > 1 else "racine"

        documents.append({
            "content": content,
            "filename": md_file.stem,
            "category": category,
            "filepath": str(relative),
        })

    return documents


def chunk_document(
    doc: dict,
    md_splitter: MarkdownHeaderTextSplitter,
    text_splitter: RecursiveCharacterTextSplitter,
 ) -> list[dict]:
    """Découpe un document Markdown en chunks enrichis."""
    content = doc["content"]
    chunks = []

    md_sections = md_splitter.split_text(content)
    if not md_sections:
        md_sections = [
            type("Section", (), {"page_content": content, "metadata": {}})()
        ]

    chunk_index = 0

    for section in md_sections:
        section_text = section.page_content
        section_metadata = section.metadata

        section_title_parts = []
        for key in ["titre_h1", "titre_h2", "titre_h3"]:
            if key in section_metadata:
                section_title_parts.append(section_metadata[key])
        section_title = " > ".join(section_title_parts) if section_title_parts else ""

        base_meta = {
            "source": doc["filepath"],
            "filename": doc["filename"],
            "category": doc["category"],
            "section": section_title,
            **section_metadata,
        }

        if len(section_text) <= CHUNK_SIZE:
            chunks.append({
                "text": section_text,
                "metadata": {
                    **base_meta,
                    "chunk_index": chunk_index,
                    "chunk_size": len(section_text),
                },
            })
            chunk_index += 1
        else:
            sub_chunks = text_splitter.split_text(section_text)
            for sub_chunk in sub_chunks:
                chunks.append({
                    "text": sub_chunk,
                    "metadata": {
                        **base_meta,
                        "chunk_index": chunk_index,
                        "chunk_size": len(sub_chunk),
                    },
                })
                chunk_index += 1

    return chunks


def run_chunking(
    input_dir: Path | None = None,
    output_file: Path | None = None,
    progress_callback: ProgressCallback | None = None,
) -> list[dict]:
    """
    Point d'entrée de l'étape 2 : chunking des documents Markdown.

    Paramètres :
        input_dir         : répertoire Markdown (défaut : config.MARKDOWN_DIR)
        output_file       : fichier JSON de sortie (défaut : config.CHUNKS_OUTPUT_FILE)
        progress_callback : fn(current, total, message)

    Retourne :
        La liste de tous les chunks générés.
    """
    input_dir = input_dir or MARKDOWN_DIR
    output_file = output_file or CHUNKS_OUTPUT_FILE

    logger.info("=" * 65)
    logger.info("✂️  ÉTAPE 2 — DÉCOUPAGE RÉCURSIF AVEC CHEVAUCHEMENT")
    logger.info("=" * 65)

    if not input_dir.exists():
        logger.error("Répertoire Markdown introuvable : %s", input_dir)
        return []

    documents = load_markdown_files(input_dir)

    if not documents:
        logger.warning("Aucun fichier Markdown trouvé !")
        return []

    logger.info("   %d documents chargés", len(documents))

    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON,
        strip_headers=False,
    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=SEPARATORS,
        length_function=len,
        is_separator_regex=False,
        add_start_index=True,
    )

    all_chunks = []
    total = len(documents)

    for idx, doc in enumerate(documents):
        if progress_callback:
            progress_callback(idx + 1, total, f"✂️  Découpage : {doc['filename']}")
        doc_chunks = chunk_document(doc, md_splitter, text_splitter)
        all_chunks.extend(doc_chunks)
        logger.info("   %-50s → %2d chunks", doc["filepath"][:50], len(doc_chunks))

    # Export JSON
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_data = {
        "config": {
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
            "separators": SEPARATORS,
            "headers_to_split_on": [h[0] for h in HEADERS_TO_SPLIT_ON],
            "total_documents": len(documents),
            "total_chunks": len(all_chunks),
        },
        "chunks": all_chunks,
    }
    output_file.write_text(
        json.dumps(output_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    logger.info("💾 %d chunks sauvegardés → %s", len(all_chunks), output_file)

    if progress_callback:
        progress_callback(total, total, f"✅ {len(all_chunks)} chunks générés")

    return all_chunks


# ── Exécution autonome ──────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, datefmt=LOG_DATEFMT)
    run_chunking()
