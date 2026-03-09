"""
Prompts système et construction des messages pour le LLM.

Pour modifier le comportement de l'assistant, éditer SYSTEM_PROMPT.
Pour changer la structure des messages, modifier build_messages.
"""

from __future__ import annotations


# ══════════════════════════════════════════════════════════════════════════════
# PROMPT SYSTÈME
# ══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """\
### RÔLE :
Vous êtes un assistant documentaire intelligent et bienveillant.
Vous répondez uniquement à partir des documents fournis par l'utilisateur.

### COMPORTEMENT :
- Répondez en français, de façon claire, structurée et précise.
- Citez toujours vos sources (noms de fichiers) si disponibles.
- Si l'information n'est pas dans les documents : dites-le clairement, ne l'inventez pas.
- Utilisez des listes et titres Markdown pour les réponses longues.

### INTERDICTIONS :
- Ne jamais inventer de faits.
- Ne jamais répondre sur des sujets non couverts par les documents.
"""


# ══════════════════════════════════════════════════════════════════════════════
# CONSTRUCTION DES MESSAGES
# ══════════════════════════════════════════════════════════════════════════════

def build_messages(history: list[dict], question: str, context: str) -> list:
    """
    Construit les messages formatés pour l'API Mistral.

    Paramètres :
        history  : historique de conversation [{role, content}, ...]
        question : question actuelle de l'utilisateur
        context  : contexte RAG (texte des documents pertinents)

    Retourne :
        Liste de messages Mistral (SystemMessage, UserMessage, AssistantMessage)
    """
    from mistralai.models import UserMessage, AssistantMessage, SystemMessage

    formatted = [SystemMessage(content=SYSTEM_PROMPT)]

    # Garder les 8 derniers messages pour le contexte
    recent = history[-8:] if len(history) > 8 else history
    for msg in recent[:-1]:
        if msg["role"] == "user":
            formatted.append(UserMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            formatted.append(AssistantMessage(content=msg["content"]))

    # Enrichir la question avec le contexte RAG si disponible
    if context:
        enriched = (
            f"### DOCUMENTS PERTINENTS :\n{context}\n\n"
            f"### QUESTION :\n{question}"
        )
    else:
        enriched = question

    formatted.append(UserMessage(content=enriched))
    return formatted
