"""
Client LLM Mistral.

Gère les appels API (streaming et synchrone).
Pour changer de modèle ou provider, modifier uniquement ce fichier.
"""

from __future__ import annotations

import logging
from typing import Generator

from streamlit.config.settings import MISTRAL_API_KEY, GENERATION_PARAMS

logger = logging.getLogger(__name__)


def stream_llm(messages: list, model: str) -> Generator[str, None, None]:
    """
    Appelle l'API Mistral en mode streaming et yield les tokens un par un.

    Paramètres :
        messages : liste de messages formatés (SystemMessage, UserMessage, etc.)
        model    : identifiant du modèle Mistral à utiliser

    Yields :
        str — chaque token de la réponse
    """
    if not MISTRAL_API_KEY:
        yield "❌ Clé API Mistral non configurée. Veuillez définir `MISTRAL_API_KEY` dans le fichier `.env`."
        return

    try:
        from mistralai import Mistral

        client = Mistral(api_key=MISTRAL_API_KEY)
        stream_resp = client.chat.stream(
            model=model,
            messages=messages,
            **GENERATION_PARAMS,
        )
        for chunk in stream_resp:
            token = chunk.data.choices[0].delta.content
            if token:
                yield token
    except Exception as e:
        logger.error("Erreur LLM : %s", e)
        yield f"❌ Erreur lors de l'appel à Mistral : {e}"


def call_llm(messages: list, model: str) -> str:
    """
    Appelle l'API Mistral en mode synchrone et retourne la réponse complète.

    Utile pour les cas où le streaming n'est pas nécessaire.
    """
    if not MISTRAL_API_KEY:
        return "❌ Clé API Mistral non configurée. Veuillez définir `MISTRAL_API_KEY` dans le fichier `.env`."

    try:
        from mistralai import Mistral

        client = Mistral(api_key=MISTRAL_API_KEY)
        resp = client.chat.complete(model=model, messages=messages, **GENERATION_PARAMS)
        if resp.choices:
            return resp.choices[0].message.content
        return "Je suis désolé, je n'ai pas pu générer de réponse."
    except Exception as e:
        logger.error("Erreur LLM : %s", e)
        return f"❌ Erreur lors de l'appel à Mistral : {e}"
