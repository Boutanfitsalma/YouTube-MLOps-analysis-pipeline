import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from datetime import datetime

st.set_page_config(page_title="YouTube Data Analysis Dashboard", layout="wide")
st.title("📊 YouTube Data Analysis Dashboard")

# Fonction pour charger les données
def load_data():
    # Obtenir le fichier le plus récent
    files = [f for f in os.listdir("/data") if f.startswith("youtube_")]
    if not files:
        st.error("Aucun fichier de données trouvé!")
        return None, None, None
    
    try:
        latest_videos = max([f for f in files if "videos" in f])
        latest_comments = max([f for f in files if "comments" in f])
        latest_analysis = max([f for f in files if "analysis" in f])
        
        # Charger les données
        with open(f"/data/{latest_videos}", "r") as f:
            videos = json.load(f)
        
        with open(f"/data/{latest_comments}", "r") as f:
            comments = json.load(f)
        
        with open(f"/data/{latest_analysis}", "r") as f:
            analysis = json.load(f)
        
        return videos, comments, analysis
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        return None, None, None

# Affichage des données d'exemple si aucune données n'est disponible
def show_example_data():
    st.info("Aucune donnée disponible. Voici un exemple de visualisation.")
    
    # Données d'exemple
    example_data = {
        "titles": ["Vidéo 1", "Vidéo 2", "Vidéo 3", "Vidéo 4", "Vidéo 5"],
        "views": [1500, 2300, 1800, 3200, 2700]
    }
    
    # Visualisation d'exemple
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(example_data["titles"], example_data["views"])
    ax.set_title("Exemple: Nombre de vues par vidéo")
    ax.set_xlabel("Titre de la vidéo")
    ax.set_ylabel("Nombre de vues")
    st.pyplot(fig)

# Charger les données
videos, comments, analysis = load_data()

if videos and comments and analysis:
    # Afficher les infos de base
    st.subheader("📈 Statistiques de la chaîne")
    col1, col2, col3 = st.columns(3)
    col1.metric("Nombre de vidéos", len(videos))
    col2.metric("Nombre de commentaires", len(comments))
    col3.metric("Dernière mise à jour", datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    # Visualisations
    st.subheader("📊 Analyse des vidéos")
    
    # Convertir en DataFrame
    videos_df = pd.DataFrame(videos)
    comments_df = pd.DataFrame(comments)
    
    # Top vidéos par vues
    fig, ax = plt.subplots(figsize=(10, 6))
    top_videos = videos_df.sort_values("viewCount", ascending=False).head(5)
    sns.barplot(x="title", y="viewCount", data=top_videos)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)
    
    # Analyse des sentiments
    st.subheader("💬 Analyse des sentiments")
    sentiment_df = pd.DataFrame(analysis["sentimentAnalysis"])
    
    fig, ax = plt.subplots(figsize=(8, 8))
    sentiment_counts = sentiment_df["label"].value_counts()
    plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct="%1.1f%%")
    plt.title("Distribution des sentiments")
    st.pyplot(fig)
    
    # Afficher les entités extraites
    st.subheader("🔍 Entités nommées extraites")
    entities_df = pd.DataFrame(analysis["namedEntities"])
    st.dataframe(entities_df)
else:
    show_example_data()
    
    # Instructions pour générer des données
    st.subheader("💡 Comment générer des données")
    st.markdown("""
    1. Accédez à n8n à l'adresse: http://localhost:5678
    2. Connectez-vous et ouvrez le workflow 'YouTube MLOps Pipeline'
    3. Cliquez sur 'Exécuter le workflow' avec le message "GoDeploy"
    4. Une fois l'exécution terminée, actualisez cette page pour voir les résultats
    """)