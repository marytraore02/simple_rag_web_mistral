"""
Classifieur d'intention pour les requêtes utilisateur.

Détermine si une question nécessite une recherche RAG (base de connaissances)
ou s'il s'agit d'une interaction conversationnelle classique (CHAT).
"""

from __future__ import annotations

import logging

from app_config.settings import MISTRAL_API_KEY

logger = logging.getLogger(__name__)

# ── Constantes d'intention ────────────────────────────────────────────────────
INTENT_RAG = "RAG"
INTENT_CHAT = "CHAT"
DEFAULT_INTENT = INTENT_RAG  # Par défaut RAG pour ne pas manquer d'info pertinente

# ── Prompt système pour la classification ─────────────────────────────────────
CLASSIFICATION_SYSTEM_PROMPT = """\
Votre rôle est de classifier l'intention de la question de l'utilisateur \
pour un chatbot d'une mairie.
Répondez UNIQUEMENT par "RAG" ou "CHAT". Ne fournissez aucune autre explication.

- Répondez "RAG" si la question cherche des informations spécifiques qui \
pourraient se trouver dans les documents de la mairie :
  • Procédures administratives (carte d'identité, passeport, acte de naissance…)
  • Horaires et adresses des services municipaux
  • Documents nécessaires pour une démarche
  • Règlements et arrêtés municipaux
  • Services municipaux (piscine, bibliothèque, crèche…)
  • Informations locales spécifiques à la commune
  • Toute question nécessitant une recherche documentaire

- Répondez "CHAT" si la question est :
  • Une salutation (Bonjour, Salut, Bonsoir…)
  • Une formule de politesse (Merci, Au revoir, Bonne journée…)
  • Une conversation générale sans rapport avec la mairie
  • Une question hors sujet pour la mairie (météo, sport, actualités nationales…)
  • Une simple interaction sociale ou bavardage

Exemples :
- "Quels papiers faut-il pour un passeport ?" → RAG
- "Bonjour comment allez-vous ?" → CHAT
- "Quels sont les horaires de la piscine municipale ?" → RAG
- "Merci beaucoup !" → CHAT
- "Parlez-moi de la météo demain" → CHAT
- "Comment inscrire mon enfant à l'école ?" → RAG
- "Bonsoir" → CHAT
- "Où se trouve le service état civil ?" → RAG
- "C'est gentil, merci pour votre aide" → CHAT
- "Quelles sont les démarches pour un mariage ?" → RAG
"""


def classify_query_intent(query: str, model: str = "mistral-small-latest") -> str:
    """
    Classifie l'intention de la requête utilisateur via l'API Mistral.

    Paramètres :
        query : la question posée par l'utilisateur
        model : le modèle Mistral à utiliser (petit modèle suffisant pour la classification)

    Retourne :
        "RAG" si la question nécessite une recherche documentaire,
        "CHAT" si c'est une interaction conversationnelle.
    """
    if not MISTRAL_API_KEY:
        logger.warning("Clé API Mistral non configurée, intention par défaut: %s", DEFAULT_INTENT)
        return DEFAULT_INTENT

    try:
        from mistralai import Mistral
        from mistralai.models import SystemMessage, UserMessage

        client = Mistral(api_key=MISTRAL_API_KEY)

        messages = [
            SystemMessage(content=CLASSIFICATION_SYSTEM_PROMPT),
            UserMessage(content=query),
        ]

        logger.info("Classification de la requête: '%s'", query[:60])

        response = client.chat.complete(
            model=model,
            messages=messages,
            temperature=0.1,   # Basse température pour une réponse déterministe
            max_tokens=5,      # On attend juste "RAG" ou "CHAT"
        )

        intent = response.choices[0].message.content.strip().upper()

        if intent == INTENT_RAG:
            logger.info("Intention détectée: %s", INTENT_RAG)
            return INTENT_RAG
        elif intent == INTENT_CHAT:
            logger.info("Intention détectée: %s", INTENT_CHAT)
            return INTENT_CHAT
        else:
            logger.warning(
                "Classification non conforme reçue: '%s'. Utilisation par défaut: %s",
                intent, DEFAULT_INTENT,
            )
            return DEFAULT_INTENT

    except Exception as e:
        logger.error("Erreur lors de la classification: %s", e)
        return DEFAULT_INTENT
