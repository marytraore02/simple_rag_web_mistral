"""
Page Visualisation — Exploration des index FAISS, chunks et embeddings.
"""

from __future__ import annotations

import json

import streamlit as st

from app_config.settings import (
    FAISS_INDEX_FILE,
    FAISS_METADATA_FILE,
    ROOT_DIR,
)
from utils.helpers import index_ready


def render(tab) -> None:
    """Affiche l'onglet Visualisation dans le conteneur `tab`."""

    with tab:
        st.markdown("""
        <div class="pipeline-card">
          <h1>📊 Visualisation des Résultats</h1>
          <p class="pipeline-subtitle">
            Explorez les embeddings, chunks et l'index vectoriel après l'exécution du pipeline
          </p>
        </div>
        """, unsafe_allow_html=True)

        if not index_ready():
            st.info(
                "💡 **Aucune donnée à visualiser pour le moment.**\n\n"
                "Lancez d'abord le pipeline dans l'onglet **⚙️ Pipeline** "
                "pour générer les données."
            )
            return

        # ── Load data ────────────────────────────────────────────────────
        viz_chunks_data = None
        viz_chunks = []
        viz_metadata = []
        viz_index = None
        viz_embeddings = None

        chunks_file = ROOT_DIR / "data" / "chunks" / "chunks.json"
        embeddings_file = ROOT_DIR / "data" / "chunks" / "embeddings.npz"

        if chunks_file.exists():
            with open(chunks_file, "r", encoding="utf-8") as f:
                viz_chunks_data = json.load(f)
                viz_chunks = viz_chunks_data.get("chunks", [])

        if FAISS_METADATA_FILE.exists():
            with open(FAISS_METADATA_FILE, "r", encoding="utf-8") as f:
                viz_metadata = json.load(f)

        try:
            import faiss
            if FAISS_INDEX_FILE.exists():
                viz_index = faiss.read_index(str(FAISS_INDEX_FILE))
        except Exception:
            pass

        if embeddings_file.exists():
            try:
                import numpy as np
                data = np.load(str(embeddings_file))
                if "sbert" in data:
                    viz_embeddings = data["sbert"]
                elif len(data.files) > 0:
                    viz_embeddings = data[data.files[0]]
            except Exception:
                pass

        # ── Stats cards ──────────────────────────────────────────────────
        st.markdown("")
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            ntotal = viz_index.ntotal if viz_index else 0
            d = viz_index.d if viz_index else '—'
            st.markdown(f"""
            <div class="viz-card">
                <h3>🗄️ Index FAISS</h3>
                <div class="viz-stat"><span class="viz-stat-label">Vecteurs</span><span class="viz-stat-value">{ntotal}</span></div>
                <div class="viz-stat"><span class="viz-stat-label">Dimensions</span><span class="viz-stat-value">{d}</span></div>
            </div>""", unsafe_allow_html=True)

        with c2:
            conf_size = viz_chunks_data.get('config', {}).get('chunk_size', '—') if viz_chunks_data else '—'
            conf_ovlp = viz_chunks_data.get('config', {}).get('chunk_overlap', '—') if viz_chunks_data else '—'
            st.markdown(f"""
            <div class="viz-card">
                <h3>✂️ Chunks</h3>
                <div class="viz-stat"><span class="viz-stat-label">Total</span><span class="viz-stat-value">{len(viz_chunks)}</span></div>
                <div class="viz-stat"><span class="viz-stat-label">Config</span><span class="viz-stat-value">{conf_size}/{conf_ovlp}</span></div>
            </div>""", unsafe_allow_html=True)

        with c3:
            n_sources = len(set(c.get("metadata", {}).get("filename", "") for c in viz_chunks)) if viz_chunks else 0
            st.markdown(f"""
            <div class="viz-card">
                <h3>📂 Sources</h3>
                <div class="viz-stat"><span class="viz-stat-label">Documents</span><span class="viz-stat-value">{n_sources}</span></div>
                <div class="viz-stat"><span class="viz-stat-label">Métadonnées</span><span class="viz-stat-value">{len(viz_metadata)}</span></div>
            </div>""", unsafe_allow_html=True)

        with c4:
            emb_shape = viz_embeddings.shape if viz_embeddings is not None else None
            shape_str = f'{emb_shape[0]}×{emb_shape[1]}' if emb_shape else '—'
            st.markdown(f"""
            <div class="viz-card">
                <h3>🧠 Embeddings</h3>
                <div class="viz-stat"><span class="viz-stat-label">Shape</span><span class="viz-stat-value">{shape_str}</span></div>
                <div class="viz-stat"><span class="viz-stat-label">Modèle</span><span class="viz-stat-value">SBERT</span></div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

        # ── Embedding Visualization ──────────────────────────────────────
        st.markdown("""
        <div class="section-header">
            <h3>🧠 Visualisation des Embeddings (2D)</h3>
        </div>
        """, unsafe_allow_html=True)

        _render_embeddings_plot(viz_embeddings, viz_chunks)

        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

        # ── Chunks Explorer ──────────────────────────────────────────────
        st.markdown("""
        <div class="section-header">
            <h3>✂️ Explorateur de Chunks</h3>
        </div>
        """, unsafe_allow_html=True)

        if viz_chunks:
            all_sources = sorted(set(c.get("metadata", {}).get("filename", "Inconnu") for c in viz_chunks))
            selected_source = st.selectbox("🔍 Filtrer par source", ["Tous"] + all_sources, key="viz_source_filter")

            filtered = viz_chunks if selected_source == "Tous" else [
                c for c in viz_chunks if c.get("metadata", {}).get("filename") == selected_source
            ]

            st.caption(f"Affichage de {min(20, len(filtered))}/{len(filtered)} chunks")

            for i, chunk in enumerate(filtered[:20]):
                meta = chunk.get("metadata", {})
                text_preview = chunk.get("text", "")[:200].replace("\n", " ")
                chunk_index = meta.get('chunk_index', i)
                filename = meta.get('filename', 'Inconnu')
                chunk_size = meta.get('chunk_size', len(chunk.get('text', '')))
                category = meta.get('category', '—')

                st.markdown(f"""
                <div class="viz-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                        <span style="font-weight:700; font-size:0.9rem;">Chunk #{chunk_index}</span>
                        <span class="file-type-tag">{filename}</span>
                    </div>
                    <div style="color:var(--text-muted); font-size:0.85rem; line-height:1.5;">{text_preview}…</div>
                    <div style="margin-top:0.5rem; display:flex; gap:1rem;">
                        <span class="stat-pill">📏 {chunk_size} car.</span>
                        <span class="stat-pill">📂 {category}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aucun chunk disponible. Lancez le pipeline d'abord.")


def _render_embeddings_plot(viz_embeddings, viz_chunks) -> None:
    """Génère et affiche le graphique 2D des embeddings avec t-SNE / PCA."""

    if viz_embeddings is None or len(viz_embeddings) < 2:
        st.info("Pas assez de données pour la visualisation 2D.")
        return

    try:
        from sklearn.manifold import TSNE
        from sklearn.decomposition import PCA
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        n_samples = len(viz_embeddings)
        if n_samples < 5:
            reducer = PCA(n_components=2, random_state=42)
            coords = reducer.fit_transform(viz_embeddings)
            method = "PCA"
        else:
            perp = min(30, n_samples - 1)
            reducer = TSNE(
                n_components=2, perplexity=perp, random_state=42,
                init="pca", learning_rate="auto"
            )
            coords = reducer.fit_transform(viz_embeddings)
            method = "t-SNE"

        filenames = [c.get("metadata", {}).get("filename", "Inconnu") for c in viz_chunks[:n_samples]]

        fig, ax = plt.subplots(figsize=(12, 7))
        fig.patch.set_facecolor('#0d0f14' if st.session_state.dark_mode else '#f5f7fb')
        ax.set_facecolor('#161b27' if st.session_state.dark_mode else '#ffffff')

        unique_files = list(set(filenames))
        colors = plt.cm.Set2.colors if len(unique_files) <= 8 else plt.cm.tab20.colors
        color_map = {f: colors[i % len(colors)] for i, f in enumerate(unique_files)}

        for fname in unique_files:
            mask = [i for i, fn in enumerate(filenames) if fn == fname]
            ax.scatter(
                coords[mask, 0], coords[mask, 1],
                label=fname, alpha=0.75, s=80, edgecolors='white', linewidths=0.5,
                color=color_map[fname],
            )
        text_color = '#e8eaf0' if st.session_state.dark_mode else '#1a1d2e'
        ax.set_title(
            f"Embeddings ({method}) — {n_samples} chunks",
            fontsize=14, fontweight="bold", color=text_color, pad=15
        )
        ax.tick_params(colors=text_color)
        for spine in ax.spines.values():
            spine.set_color('#2d3148' if st.session_state.dark_mode else '#d0d5e8')
        ax.legend(fontsize=8, loc="upper right", framealpha=0.7)
        fig.tight_layout()

        st.pyplot(fig)
        plt.close(fig)

    except Exception as e:
        st.warning(f"Impossible de générer la visualisation : {e}")
