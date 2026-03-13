"""
Sidebar de l'application — Logo, thème, modèle LLM, actions.
"""

from __future__ import annotations

import streamlit as st

from app_config.settings import AVAILABLE_MODELS, MISTRAL_API_KEY
from ui.theme import inject_theme_css
from utils.helpers import index_ready, complete_reset


def render_sidebar() -> None:
    """Affiche la sidebar complète de l'application."""

    with st.sidebar:
        dark = st.session_state.dark_mode
        inject_theme_css(dark)

        # ── Logo & titre ─────────────────────────────────────────────────
        st.markdown("""
        <div style="text-align:center; padding: 1rem 0 .5rem;">
            <div style="font-size:2.8rem">🧠</div>
            <div style="font-size:1.15rem; font-weight:800;
                 background:linear-gradient(90deg,#6c63ff,#00d4aa);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                RAG Web App
            </div>
            <div style="color:#8b92a5; font-size:.8rem; margin-top:.2rem;">
                Mistral · FAISS · Docling
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Thème ────────────────────────────────────────────────────────
        theme_label = "☀️ Mode Clair" if dark else "🌙 Mode Sombre"
        if st.button(theme_label, use_container_width=True):
            st.session_state.dark_mode = not dark
            st.rerun()

        st.divider()

        # ── Statut de l'index ────────────────────────────────────────────
        if index_ready():
            st.markdown(
                '<span class="badge badge-green">✅ Index FAISS prêt</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="badge badge-yellow">⚠️ Index non construit</span>',
                unsafe_allow_html=True,
            )

        n_files = len(st.session_state.uploaded_files_meta)
        st.caption(f"📂 {n_files} fichier(s) chargé(s)")

        # ── Sélecteur de modèle LLM ─────────────────────────────────────
        st.divider()
        st.markdown("**⚙️ Modèle LLM**")
        model_labels = list(AVAILABLE_MODELS.keys())
        sel_label = st.selectbox(
            "Modèle",
            model_labels,
            index=model_labels.index(
                next(
                    (k for k, v in AVAILABLE_MODELS.items()
                     if v == st.session_state.rag_model),
                    model_labels[0],
                )
            ),
            label_visibility="collapsed",
        )
        st.session_state.rag_model = AVAILABLE_MODELS[sel_label]
        # st.caption(f"📡 `{st.session_state.rag_model}`")

        # ── Actions ──────────────────────────────────────────────────────
        st.divider()
        if st.button("🗑️ Effacer la conversation", use_container_width=True):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "👋 Conversation effacée. Comment puis-je vous aider ?",
                }
            ]
            st.rerun()

        if st.button("🔄 Réinitialiser complètement (Hard Reset)", use_container_width=True, type="secondary"):
            complete_reset()
            st.rerun()

        st.divider()
        st.caption(
            "🔑 API Mistral : " + ("✅ configurée" if MISTRAL_API_KEY else "❌ manquante")
        )
