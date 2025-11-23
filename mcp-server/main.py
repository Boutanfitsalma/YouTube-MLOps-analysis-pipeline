from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import torch
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mcp_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mcp-server")

# Chemin pour sauvegarder les modèles
MODELS_DIR = os.path.join(os.getcwd(), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Chemin pour les données
DATA_DIR = "/data"
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

app = FastAPI(title="MCP Server for YouTube Analysis")

# Modèles Hugging Face
sentiment_analyzer = None
text_classifier = None
ner_pipeline = None

# Classes pour les requêtes API
class TextInput(BaseModel):
    text: str

class BatchTextInput(BaseModel):
    texts: List[str]

class ModelConfig(BaseModel):
    model_name: str
    task: str

class AnalysisResult(BaseModel):
    result: Any
    timestamp: str

# Fonction pour charger les modèles (exécutée au démarrage)
def load_models():
    global sentiment_analyzer, text_classifier, ner_pipeline
    
    logger.info("Chargement des modèles Hugging Face...")
    
    try:
        # Modèle d'analyse de sentiment
        sentiment_model_path = os.path.join(MODELS_DIR, "sentiment-analysis")
        if os.path.exists(sentiment_model_path):
            sentiment_analyzer = pipeline("sentiment-analysis", model=sentiment_model_path)
        else:
            sentiment_analyzer = pipeline("sentiment-analysis")
            # Sauvegarder le modèle pour usage futur
            sentiment_analyzer.save_pretrained(sentiment_model_path)
        
        # Modèle de classification de texte
        classifier_model_path = os.path.join(MODELS_DIR, "text-classification")
        if os.path.exists(classifier_model_path):
            text_classifier = pipeline("text-classification", model=classifier_model_path)
        else:
            text_classifier = pipeline("text-classification", model="facebook/bart-large-mnli")
            text_classifier.save_pretrained(classifier_model_path)
        
        # Modèle NER (Named Entity Recognition)
        ner_model_path = os.path.join(MODELS_DIR, "ner")
        if os.path.exists(ner_model_path):
            ner_pipeline = pipeline("ner", model=ner_model_path)
        else:
            ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")
            ner_pipeline.save_pretrained(ner_model_path)
        
        logger.info("Tous les modèles ont été chargés avec succès!")
    
    except Exception as e:
        logger.error(f"Erreur lors du chargement des modèles: {str(e)}")
        raise

# Point de terminaison racine
@app.get("/")
async def root():
    return {
        "message": "MCP Server for YouTube Data Analysis",
        "status": "running",
        "models_loaded": {
            "sentiment_analyzer": sentiment_analyzer is not None,
            "text_classifier": text_classifier is not None,
            "ner_pipeline": ner_pipeline is not None
        }
    }

# Analyse de sentiment
@app.post("/sentiment", response_model=AnalysisResult)
async def analyze_sentiment(input_data: TextInput):
    try:
        if sentiment_analyzer is None:
            load_models()
        
        result = sentiment_analyzer(input_data.text)
        logger.info(f"Sentiment analysis performed: {result}")
        
        return {
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")

# Classification de texte
@app.post("/classify", response_model=AnalysisResult)
async def classify_text(input_data: TextInput):
    try:
        if text_classifier is None:
            load_models()
        
        result = text_classifier(input_data.text)
        logger.info(f"Text classification performed: {result}")
        
        return {
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error classifying text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error classifying text: {str(e)}")

# Extraction d'entités nommées
@app.post("/ner", response_model=AnalysisResult)
async def extract_entities(input_data: TextInput):
    try:
        if ner_pipeline is None:
            load_models()
        
        result = ner_pipeline(input_data.text)
        logger.info(f"Named entity recognition performed")
        
        return {
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error extracting entities: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting entities: {str(e)}")

# Analyse de sentiment par lots
@app.post("/batch-sentiment", response_model=AnalysisResult)
async def batch_analyze_sentiment(input_data: BatchTextInput, background_tasks: BackgroundTasks):
    try:
        if sentiment_analyzer is None:
            load_models()
        
        # Pour les grands lots, on limite à 100 textes pour éviter des timeouts
        texts_to_analyze = input_data.texts[:100]
        
        result = sentiment_analyzer(texts_to_analyze)
        logger.info(f"Batch sentiment analysis performed on {len(texts_to_analyze)} texts")
        
        # Si le lot est grand, programmer l'analyse complète en arrière-plan
        if len(input_data.texts) > 100:
            background_tasks.add_task(
                process_full_batch, 
                input_data.texts, 
                "sentiment"
            )
        
        return {
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error batch analyzing sentiment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error batch analyzing sentiment: {str(e)}")

# Traiter un lot complet en arrière-plan
async def process_full_batch(texts, analysis_type):
    try:
        timestamp = datetime.now().isoformat().replace(":", "-")
        filename = f"{analysis_type}_full_batch_{timestamp}.json"
        filepath = os.path.join(PROCESSED_DIR, filename)
        
        logger.info(f"Processing full batch of {len(texts)} texts for {analysis_type} analysis")
        
        if analysis_type == "sentiment":
            # Traiter par petits lots pour éviter les problèmes de mémoire
            batch_size = 32
            results = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                batch_results = sentiment_analyzer(batch)
                results.extend(batch_results)
            
            # Sauvegarder les résultats
            with open(filepath, 'w') as f:
                json.dump(results, f)
            
            logger.info(f"Full batch processing completed and saved to {filepath}")
    
    except Exception as e:
        logger.error(f"Error in background processing: {str(e)}")

# Charger les modèles au démarrage
@app.on_event("startup")
async def startup_event():
    try:
        load_models()
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")