"""
Page Pipeline — Lancement et suivi du pipeline RAG.
"""

from __future__ import annotations

import time

import streamlit as st

from app_config.settings import MISTRAL_API_KEY


def render(tab) -> None:
    """Affiche l'onglet Pipeline dans le conteneur `tab`."""

    with tab:
        from pipeline_runner import PipelineStatus, run_pipeline_async

        ps: PipelineStatus | None = st.session_state.pipeline_status
        snap = ps.snapshot() if ps else None

        is_running = bool(snap and snap["running"])
        is_done = bool(snap and snap["done"])
        has_error = bool(snap and snap["error"])

        # ── Pipeline Card ────────────────────────────────────────────────
        st.markdown("""
        <div class="pipeline-card">
          <h1>⚙️ Pipeline RAG</h1>
          <p class="pipeline-subtitle">
            Transformez vos documents en une base de connaissances interrogeable
          </p>
        """, unsafe_allow_html=True)

        # ── Les 4 étapes en grille ───────────────────────────────────────
        steps_info = [
            ("1", "Extraction",  "Docling + Whisper → Markdown",           "📄"),
            ("2", "Chunking",    "Découpage récursif + chevauchement",      "✂️"),
            ("3", "Embeddings",  "SBERT (+ Mistral optionnel) → vecteurs",  "🧠"),
            ("4", "Indexation",  "FAISS IndexFlatIP → recherche cosine",    "🗄️"),
        ]

        current_step = snap["current_step"] if snap else 0

        steps_html = '<div class="steps-grid">'
        for num, label, desc, icon in steps_info:
            n = int(num)
            if is_done or (snap and current_step > n):
                css_class = "done"
                indicator = "✅"
            elif snap and current_step == n and is_running:
                css_class = "active"
                indicator = "⏳"
            else:
                css_class = "pending"
                indicator = num

            steps_html += f"""
            <div class="step-card {css_class}">
              <div class="step-icon">{icon}</div>
              <div class="step-num-badge">{indicator}</div>
              <div class="step-card-label">{label}</div>
              <div class="step-card-desc">{desc}</div>
            </div>"""
        steps_html += '</div>'

        st.markdown(steps_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Paramètre : Mistral embeddings ───────────────────────────────
        st.markdown("")

        n_files = len(st.session_state.uploaded_files_meta)

        if n_files == 0:
            st.warning(
                "⚠️ Aucun fichier chargé. Allez d'abord dans **📂 Sources** "
                "pour uploader vos documents."
            )

        use_mistral_emb = st.checkbox(
            "🌐 Utiliser Mistral pour les embeddings (plus puissant, consomme des crédits API)",
            value=False,
            disabled=not MISTRAL_API_KEY,
        )

        # ── Gros bouton Lancer ───────────────────────────────────────────
        st.markdown("")

        btn_label = "🔄 Relancer le pipeline" if is_done else "🚀 Lancer le pipeline"

        # Status badge
        if is_running:
            st.markdown(
                '<center><span class="badge badge-blue" style="font-size:0.9rem; padding:0.4rem 1rem;">'
                "⏳ Pipeline en cours d'exécution…</span></center>",
                unsafe_allow_html=True,
            )
        elif is_done:
            st.markdown(
                '<center><span class="badge badge-green" style="font-size:0.9rem; padding:0.4rem 1rem;">'
                "✅ Pipeline terminé avec succès</span></center>",
                unsafe_allow_html=True,
            )
        elif has_error:
            st.markdown(
                '<center><span class="badge badge-red" style="font-size:0.9rem; padding:0.4rem 1rem;">'
                "❌ Erreur lors de l'exécution</span></center>",
                unsafe_allow_html=True,
            )

        st.markdown("")
        st.markdown('<div class="launch-btn-wrap pulse-btn">', unsafe_allow_html=True)
        if st.button(
            btn_label,
            disabled=(n_files == 0 or is_running),
            type="primary",
            use_container_width=True,
        ):
            new_ps = PipelineStatus()
            st.session_state.pipeline_status = new_ps
            file_paths = [m["path"] for m in st.session_state.uploaded_files_meta.values()]
            t = run_pipeline_async(file_paths, new_ps, use_mistral_embed=use_mistral_emb)
            st.session_state.pipeline_thread = t
            st.session_state.show_success_popup = False
            time.sleep(0.3)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Barre de progression ─────────────────────────────────────────
        st.markdown("")

        if snap:
            if is_running:
                overall = (snap["current_step"] - 1) / snap["total_steps"] + \
                          (snap["step_progress"] / max(snap["step_total"], 1)) / snap["total_steps"]
                st.progress(
                    min(overall, 0.99),
                    text=f"Étape {snap['current_step']}/{snap['total_steps']} — {snap['step_message']}",
                )

            elif is_done:
                st.progress(1.0, text="✅ Pipeline terminé !")
                st.success(f"🎉 Index construit avec succès — **{snap['total_vectors']} vecteurs** indexés")

                # Résumé post-pipeline
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    st.metric("📂 Fichiers traités", len(st.session_state.uploaded_files_meta))
                with m_col2:
                    st.metric("🗄️ Vecteurs indexés", snap["total_vectors"])
                with m_col3:
                    st.metric("📡 Embedding", "SBERT" + (" + Mistral" if use_mistral_emb else ""))

                # ── Success banner ───────────────────────────────────────
                st.markdown("""
                <div style="margin-top:1.5rem; padding:1.5rem 2rem; border-radius:16px;
                            background: linear-gradient(135deg, rgba(0,169,143,0.12), rgba(108,99,255,0.08));
                            border: 1px solid rgba(0,212,170,0.3); text-align:center;">
                    <div style="font-size:2.5rem; margin-bottom:0.5rem;">🎉</div>
                    <div style="font-size:1.3rem; font-weight:800;
                                background:linear-gradient(90deg,#00a98f,var(--accent));
                                -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                                margin-bottom:0.4rem;">Pipeline terminé avec succès !</div>
                    <div style="color:var(--text-muted); margin-bottom:1rem;">
                        Votre base de connaissances est prête. Discutez avec vos documents dès maintenant !
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<div class="pulse-btn" style="margin-top:1rem;">', unsafe_allow_html=True)
                if st.button("💬 Aller au Chat →", use_container_width=True, type="primary", key="go_chat_btn"):
                    st.components.v1.html("""
                    <script>
                    const tabs = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
                    if (tabs.length >= 3) { tabs[2].click(); }
                    </script>
                    """, height=0)
                st.markdown('</div>', unsafe_allow_html=True)

            elif has_error:
                st.error(snap["error"])
                st.progress(0.0)
        else:
            st.progress(0.0, text="En attente du lancement…")

        # ── Journal d'exécution ──────────────────────────────────────────
        st.markdown("")
        st.markdown("""
        <div class="section-header">
            <h3>🖥️ Journal d'exécution</h3>
        </div>
        """, unsafe_allow_html=True)

        if snap and snap["logs"]:
            log_lines = snap["logs"][-100:]
            log_text = "\n".join(log_lines)
            st.markdown(f'<div class="log-box">{log_text}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="log-box" style="text-align:center; color:var(--text-muted); padding:2rem;">'
                '📋 Les logs apparaîtront ici une fois le pipeline lancé…</div>',
                unsafe_allow_html=True,
            )

        # Auto-refresh pendant l'exécution
        if is_running:
            time.sleep(1.0)
            st.rerun()
