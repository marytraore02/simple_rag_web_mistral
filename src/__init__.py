"""Package src — Modules du pipeline RAG."""

from pathlib import Path
import sys

# Expose la racine du projet pour tous les sous-modules
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
