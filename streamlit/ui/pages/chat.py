"""
Page Chat — Assistant RAG conversationnel avec streaming.
"""

from __future__ import annotations

import streamlit as st

from llm.client import stream_llm
from llm.prompts import build_messages
from llm.rag import get_rag_context
from utils.helpers import index_ready


def render(tab) -> None:
    """Affiche l'onglet Chat dans le conteneur `tab`."""

    with tab:
        # ── Header Chat ──────────────────────────────────────────────────
        st.markdown("""
        <div class="chat-welcome">
          <h1>💬 Assistant RAG</h1>
          <p class="chat-subtitle">
            Posez vos questions sur les documents indexés — les réponses citent leurs sources
          </p>
          <div class="chat-feature-grid">
            <div class="chat-feature">
              <div class="feat-icon">🔍</div>
              <div class="feat-title">Recherche sémantique</div>
              <div class="feat-desc">Trouve les passages pertinents dans vos documents</div>
            </div>
            <div class="chat-feature">
              <div class="feat-icon">📚</div>
              <div class="feat-title">Sources citées</div>
              <div class="feat-desc">Chaque réponse cite les documents utilisés</div>
            </div>
            <div class="chat-feature">
              <div class="feat-icon">🧠</div>
              <div class="feat-title">Mistral AI</div>
              <div class="feat-desc">Propulsé par les modèles Mistral de dernière génération</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Vérification de l'index ──────────────────────────────────────
        if not index_ready():
            st.info(
                "💡 **L'index FAISS n'est pas encore construit.**\n\n"
                "Pour l'utiliser :\n"
                "1. Uploadez vos documents dans **📂 Sources**\n"
                "2. Lancez le traitement dans **⚙️ Pipeline**\n"
                "3. Revenez ici pour discuter !\n\n"
                "_Le chat fonctionne également sans index (mode conversationnel)._"
            )

        # ── Affichage de l'historique ────────────────────────────────────
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # ── Saisie utilisateur ───────────────────────────────────────────
        if prompt := st.chat_input("Posez votre question sur vos documents…"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Recherche RAG
            with st.spinner("🔍 Recherche dans les documents…"):
                ctx_text, sources = get_rag_context(prompt)

            # Construire les messages
            prompt_messages = build_messages(st.session_state.messages, prompt, ctx_text)

            # Générer la réponse en streaming (mot par mot)
            with st.chat_message("assistant"):
                answer = st.write_stream(
                    stream_llm(prompt_messages, st.session_state.rag_model)
                )

                if sources:
                    sources_md = ", ".join([f"`{s}`" for s in sources])
                    st.caption(f"📚 **Sources utilisées :** {sources_md}")
                    answer += f"\n\n*📚 Sources : {', '.join(sources)}*"
                elif not ctx_text and index_ready():
                    st.caption("ℹ️ Aucun document pertinent trouvé pour cette question.")

            st.session_state.messages.append({"role": "assistant", "content": answer})
