import numpy as np
import pandas as pd
import json
import faiss
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from pathlib import Path
import warnings

# Ignorer les avertissements mineurs
warnings.filterwarnings("ignore")

# ── Chemins ─────────────────────────────────────────────────────────────
VECTORSTORE_DIR = Path("data/vectorstore")
FAISS_INDEX_FILE = VECTORSTORE_DIR / "faiss_index.bin"
FAISS_METADATA_FILE = VECTORSTORE_DIR / "metadata.json"
OUTPUT_PLOT = "faiss_visualization.png"

def main():
    if not FAISS_INDEX_FILE.exists() or not FAISS_METADATA_FILE.exists():
        print("❌ L'index FAISS ou les métadonnées sont introuvables. Assurez-vous que la base est construite.")
        return

    # 1. Charger les métadonnées
    with open(FAISS_METADATA_FILE, "r", encoding="utf-8") as f:
        metadata_list = json.load(f)

    # 2. Charger l'index FAISS
    index = faiss.read_index(str(FAISS_INDEX_FILE))
    
    print("-" * 50)
    print(f"📊 Statistiques de la base FAISS :")
    print(f"   • Nombre de vecteurs (chunks) : {index.ntotal}")
    print(f"   • Dimension des embeddings    : {index.d}")
    print("-" * 50)

    if index.ntotal < 2:
        print("❌ Pas assez de vecteurs pour générer une visualisation 2D.")
        return

    # 3. Extraire les vecteurs
    print("⏳ Extraction des vecteurs...")
    try:
        # Tente de reconstruire depuis l'index FAISS directement
        vectors = np.array([index.reconstruct(i) for i in range(index.ntotal)])
    except Exception as e:
        print(f"⚠️ Impossible de reconstruire depuis l'index FAISS (type d'index non supporté par default pour reconstruct) : {e}")
        print("⏳ Redimensionnement avec embeddings.npz...")
        try:
            embeddings_data = np.load("data/chunks/embeddings.npz")
            vectors = embeddings_data["embeddings"]
            if len(vectors) != index.ntotal:
                print("⚠️ Le nombre de vecteurs dans npz et FAISS diffère.")
        except Exception as e2:
            print(f"❌ Impossible de charger les vecteurs : {e2}")
            return

    # 4. Réduction de dimension (t-SNE ou PCA selon le nombre de points)
    n_samples = len(vectors)
    print(f"⏳ Réduction des {index.d} dimensions en 2D pour la visualisation...")
    
    if n_samples < 5:
        # Trop peu de données pour t-SNE, on utilise PCA
        reducer = PCA(n_components=2, random_state=42)
        vectors_2d = reducer.fit_transform(vectors)
        method = "PCA"
    else:
        perplexity = min(30, n_samples - 1)
        reducer = TSNE(n_components=2, perplexity=perplexity, random_state=42, init="pca", learning_rate="auto")
        vectors_2d = reducer.fit_transform(vectors)
        method = "t-SNE"

    # 5. Préparation des données pour le graphe
    df = pd.DataFrame(vectors_2d, columns=["x", "y"])
    
    # Extraire les noms de fichiers pour les couleurs
    filenames = []
    texts = []
    for m in metadata_list:
        fname = m.get("metadata", {}).get("filename", "Inconnu")
        filenames.append(fname)
        
        # Petit aperçu texte
        txt = m.get("text", "")[:40].replace("\n", " ") + "..."
        texts.append(txt)
        
    df["filename"] = filenames
    df["preview"] = texts

    # 6. Création du graphe avec Seaborn/Matplotlib
    plt.figure(figsize=(14, 9))
    sns.set_theme(style="whitegrid")
    
    plot = sns.scatterplot(
        data=df,
        x="x",
        y="y",
        hue="filename",
        palette="husl",
        s=150,     # Taille des points
        alpha=0.8, # Transparence
        edgecolor="w",
    )

    # Ajouter le numéro de l'index sur le graphe (optionnel, utile pour repérer)
    for i in range(len(df)):
        plt.text(df.x[i] + 0.02, df.y[i] + 0.02, str(i), fontsize=8, alpha=0.6)

    plt.title(f"Visualisation des Embeddings FAISS ({method})", fontsize=16, fontweight="bold", pad=20)
    plt.xlabel("Dimension 1")
    plt.ylabel("Dimension 2")
    
    # Légende en dehors du graphique
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Fichiers Sources", borderaxespad=0.)
    
    # Message expliquant ce que sont les points
    plt.figtext(0.5, 0.01, f"Chaque point ({df.shape[0]} au total) représente un chunk de texte indexé dans FAISS.", 
                wrap=True, horizontalalignment='center', fontsize=10, style='italic')

    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT, dpi=300, bbox_inches="tight")
    
    print("✅ Visualisation terminée !")
    print(f"📸 Image sauvegardée sous le nom : {OUTPUT_PLOT}")
    print("\n💡 Pour voir l'image dans l'interface, vous pouvez l'ouvrir avec un visualiseur d'images ou l'ajouter à Streamlit.")

if __name__ == "__main__":
    main()
