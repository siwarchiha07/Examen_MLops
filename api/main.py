import sys
import os
import pandas as pd
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware

# --- 1. CONFIGURATION DES CHEMINS POUR DOCKER ---
# Dans Docker, le fichier est dans /app/api/main.py
# On définit root_dir comme étant /app
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

if root_dir not in sys.path:
    sys.path.append(root_dir)

# Importation de vos modules NLP situés dans /app/src/
from src.matching import TalentSearcher
from src.agent import extract_skills, generate_summary, score_with_context
from api.model_manager import ModelManager

# Configuration MLflow
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")

app = FastAPI(title="Talent Hunter NLP API", version="2.0")

# Configuration CORS pour permettre au Frontend de communiquer avec l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. INITIALISATION ET CHARGEMENT DES DONNÉES ---
# Le chemin pointe vers /app/data/processed/profiles_enriched.csv
PROFILES_PATH = os.path.join(root_dir, "data", "processed", "profiles_enriched.csv")
full_profiles_df = pd.DataFrame() 

def load_data():
    global full_profiles_df
    try:
        if os.path.exists(PROFILES_PATH):
            full_profiles_df = pd.read_csv(PROFILES_PATH)
            print(f"[OK] {len(full_profiles_df)} profils chargés depuis {PROFILES_PATH}")
        else:
            print(f"[AVERTISSEMENT] Fichier non trouvé : {PROFILES_PATH}")
            full_profiles_df = pd.DataFrame()
    except Exception as e:
        print(f"[ERREUR] Échec du chargement CSV : {e}")

# Chargement au démarrage
load_data()
searcher = TalentSearcher()

# Initialisation du gestionnaire de modèles avec versioning MLflow
model_manager = ModelManager(mlflow_tracking_uri=MLFLOW_TRACKING_URI)
try:
    model_manager.load_latest_model()
    print("[API] Modèle MLflow chargé avec succès")
except Exception as e:
    print(f"[API] Erreur lors du chargement MLflow, utilisation du modèle par défaut: {e}")

# --- 3. MODÈLES DE DONNÉES (Pydantic) ---
class SearchRequest(BaseModel):
    job_description: str
    top_k: int = 5
    min_stars: Optional[int] = 0
    language_filter: Optional[str] = None

class PredictRequest(BaseModel):
    text: str
    model_version: Optional[str] = None  # Version du modèle (None = dernière)

class SimilarityRequest(BaseModel):
    text1: str
    text2: str
    model_version: Optional[str] = None

# --- 4. ENDPOINTS ---

@app.get("/")
async def root():
    return {"message": "API Talent Hunter NLP opérationnelle", "status": "online"}

@app.post("/agent_search")
async def agent_search(payload: SearchRequest):
    global full_profiles_df

    # Lancement de la recherche via le module src.matching
    results_df = searcher.search(
        job_description=payload.job_description,
        top_k=payload.top_k,
        min_stars=payload.min_stars,
        language_filter=payload.language_filter,
    )

    if results_df is None or results_df.empty:
        return {"results": []}

    # Nettoyage des données pour JSON
    results_df = results_df.fillna(0.0)
    records = results_df.to_dict(orient="records")
    enriched_results = []

    for r in records:
        # Sécurité pour les valeurs non-compatibles JSON (NaN/Inf)
        for key, value in r.items():
            if isinstance(value, float) and (pd.isna(value) or value == float('inf')):
                r[key] = 0.0

        # Récupération du profil complet pour enrichissement IA
        if not full_profiles_df.empty:
            profile_row = full_profiles_df[full_profiles_df['login'] == r['login']]
            
            if not profile_row.empty:
                full_text = str(profile_row['profile_text'].values[0])
                try:
                    # Appels aux fonctions de src.agent
                    r["ai_skills"] = extract_skills(full_text)
                    r["ai_summary"] = generate_summary(full_text)
                    
                    score = score_with_context(
                        {"skills": r["ai_skills"], "raw_text": full_text}, 
                        payload.job_description
                    )
                    r["agent_score"] = float(score)
                except Exception as e:
                    print(f"[INFO] Erreur IA pour {r.get('login')}: {e}")
                    r["ai_skills"] = []
                    r["ai_summary"] = "Analyse indisponible"
                    r["agent_score"] = float(r.get("similarity", 0.0))
        
        enriched_results.append(r)

    # Tri par score d'agent (IA)
    enriched_results.sort(key=lambda x: x.get("agent_score", 0), reverse=True)

    # Mise à jour optionnelle du CSV (Traçabilité demandée dans le cahier des charges)
    try:
        for r in enriched_results:
            if not full_profiles_df.empty:
                full_profiles_df.loc[full_profiles_df['login'] == r['login'], 'agent_score'] = r['agent_score']
        
        # On s'assure que le dossier existe avant de sauvegarder
        os.makedirs(os.path.dirname(PROFILES_PATH), exist_ok=True)
        full_profiles_df.to_csv(PROFILES_PATH, index=False)
    except Exception as e:
        print(f"[ERREUR] Impossible de sauvegarder les scores : {e}")

    return {"results": enriched_results}


@app.post("/predict")
async def predict(payload: PredictRequest):
    """
    Endpoint /predict : Génère l'embedding d'un texte
    Supporte le versioning des modèles via le paramètre model_version
    """
    try:
        embedding = model_manager.predict_embedding(
            payload.text,
            model_version=payload.model_version
        )
        
        model_info = model_manager.get_model_info()
        
        return {
            "text": payload.text,
            "embedding_dim": len(embedding),
            "embedding": embedding.tolist(),
            "model_version": payload.model_version or model_info["model_version"],
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction: {str(e)}")


@app.post("/predict/similarity")
async def predict_similarity(payload: SimilarityRequest):
    """
    Calcule la similarité cosinus entre deux textes
    """
    try:
        similarity = model_manager.predict_similarity(
            payload.text1,
            payload.text2,
            model_version=payload.model_version
        )
        
        model_info = model_manager.get_model_info()
        
        return {
            "text1": payload.text1,
            "text2": payload.text2,
            "similarity": similarity,
            "model_version": payload.model_version or model_info["model_version"],
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul de similarité: {str(e)}")


@app.get("/models/info")
async def get_model_info():
    """
    Retourne les informations sur les modèles disponibles
    """
    return model_manager.get_model_info()


@app.post("/models/load/{version}")
async def load_model_version(version: str):
    """
    Charge une version spécifique du modèle
    Permet de basculer entre v1 et v2 sans redémarrer l'API
    """
    try:
        model_manager.load_model_version(version)
        return {
            "message": f"Modèle version {version} chargé avec succès",
            "model_version": version,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Version {version} non trouvée: {str(e)}")


@app.get("/health")
async def health_check():
    """
    Vérification de l'état de l'API et des dépendances
    """
    health_status = {
        "api": "healthy",
        "mlflow": "unknown",
        "model": "unknown"
    }
    
    # Vérifier MLflow
    try:
        import mlflow
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        client = mlflow.tracking.MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
        experiments = client.search_experiments()
        health_status["mlflow"] = "healthy"
    except Exception as e:
        health_status["mlflow"] = f"unhealthy: {str(e)}"
    
    # Vérifier le modèle
    try:
        if model_manager.current_model is not None:
            health_status["model"] = "loaded"
        else:
            health_status["model"] = "not_loaded"
    except Exception as e:
        health_status["model"] = f"error: {str(e)}"
    
    return health_status