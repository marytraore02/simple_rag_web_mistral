"""
Configuration centralisée du pipeline RAG Web.

Toutes les constantes, chemins et paramètres sont regroupés ici
pour faciliter la maintenance et l'expérimentation.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# ── Chemins du projet ────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent

# Données (stockage local de l'app)
DATA_DIR = PROJECT_ROOT / "data"

# Répertoire dans lequel les fichiers uploadés sont copiés
INPUTS_DIR = DATA_DIR / "inputs"

# Données intermédiaires & de sortie
MARKDOWN_DIR = DATA_DIR / "markdown"
CHUNKS_DIR = DATA_DIR / "chunks"
VECTORSTORE_DIR = DATA_DIR / "vectorstore"

# Résultats d'analyse (plots, rapports)
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
PLOTS_DIR = OUTPUTS_DIR / "plots"

# ── Étape 1 : Extraction (Docling + Whisper) ────────────────────────────────

# Extensions traitées par Docling
DOCLING_EXTENSIONS = {
    ".pdf", ".docx", ".pptx", ".xlsx", ".html", ".htm",
    ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp",
    ".csv", ".tex", ".vtt",
}

# Extensions audio traitées par Faster-Whisper
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm"}

# Union de toutes les extensions supportées
SUPPORTED_EXTENSIONS = DOCLING_EXTENSIONS | AUDIO_EXTENSIONS

# Configuration Whisper
WHISPER_MODEL_SIZE = "small"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"
WHISPER_BEAM_SIZE = 5

# ── Étape 2 : Chunking ──────────────────────────────────────────────────────

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300

HEADERS_TO_SPLIT_ON = [
    ("#", "titre_h1"),
    ("##", "titre_h2"),
    ("###", "titre_h3"),
]

SEPARATORS = ["\n\n", "\n", ". ", ", ", " ", ""]

CHUNKS_OUTPUT_FILE = CHUNKS_DIR / "chunks.json"

# ── Étape 3 : Embeddings ────────────────────────────────────────────────────

SBERT_MODEL_NAME = "all-MiniLM-L6-v2"
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_EMBED_MODEL = "mistral-embed"
MISTRAL_BATCH_SIZE = 50
EMBEDDINGS_OUTPUT_FILE = CHUNKS_DIR / "embeddings.npz"

# ── Étape 4 : Vector Store (FAISS) ──────────────────────────────────────────

FAISS_INDEX_FILE = VECTORSTORE_DIR / "faiss_index.bin"
FAISS_METADATA_FILE = VECTORSTORE_DIR / "metadata.json"
FAISS_TOP_K = 5

# ── LLM ──────────────────────────────────────────────────────────────────────

AVAILABLE_MODELS = {
    "Mistral Small (rapide, économique)": "mistral-small-latest",
    "Mistral Large (puissant, précis)": "mistral-large-latest",
}

DEFAULT_MODEL = "mistral-small-latest"

GENERATION_PARAMS = {
    "temperature": 0.2,      # Factuel, peu créatif
    "top_p": 0.9,            # Cohérent, filtre les options improbables
    "max_tokens": 500,       # Réponses concises
}
# ── Logging ──────────────────────────────────────────────────────────────────

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s │ %(levelname)-7s │ %(message)s"
LOG_DATEFMT = "%H:%M:%S"
    