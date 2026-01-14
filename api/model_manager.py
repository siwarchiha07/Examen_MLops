"""
Gestionnaire de modèles avec versioning MLflow
"""
import os
import mlflow
import mlflow.sentence_transformers
from sentence_transformers import SentenceTransformer
from typing import Optional, Dict
import pandas as pd
import numpy as np


class ModelManager:
    """
    Gestionnaire pour charger et gérer les versions de modèles depuis MLflow
    """
    
    def __init__(self, mlflow_tracking_uri: str = "http://localhost:5000"):
        """
        Initialise le gestionnaire de modèles
        
        Args:
            mlflow_tracking_uri: URI du serveur MLflow
        """
        self.mlflow_tracking_uri = mlflow_tracking_uri
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        self.current_model: Optional[SentenceTransformer] = None
        self.current_model_version: Optional[str] = None
        self.model_cache: Dict[str, SentenceTransformer] = {}
    
    def load_latest_model(self, model_name: str = "embedding_model") -> SentenceTransformer:
        """
        Charge la dernière version du modèle depuis MLflow
        
        Args:
            model_name: Nom du modèle dans MLflow
            
        Returns:
            Modèle SentenceTransformer chargé
        """
        try:
            # Récupérer le dernier modèle depuis MLflow
            client = mlflow.tracking.MlflowClient(tracking_uri=self.mlflow_tracking_uri)
            
            # Chercher le dernier run avec ce modèle
            experiments = client.search_experiments()
            latest_run = None
            latest_run_id = None
            
            for exp in experiments:
                runs = client.search_runs(
                    experiment_ids=[exp.experiment_id],
                    order_by=["start_time DESC"],
                    max_results=1
                )
                if runs:
                    run = runs[0]
                    # Vérifier si ce run a le modèle
                    artifacts = client.list_artifacts(run.info.run_id)
                    if any(model_name in artifact.path for artifact in artifacts):
                        latest_run = run
                        latest_run_id = run.info.run_id
                        break
            
            if latest_run_id:
                model_uri = f"runs:/{latest_run_id}/{model_name}"
                print(f"[ModelManager] Chargement du modèle depuis: {model_uri}")
                
                model = mlflow.sentence_transformers.load_model(model_uri)
                self.current_model = model
                self.current_model_version = latest_run_id
                self.model_cache[latest_run_id] = model
                
                print(f"[ModelManager] Modèle chargé avec succès (version: {latest_run_id})")
                return model
            else:
                print("[ModelManager] Aucun modèle trouvé dans MLflow, utilisation du modèle par défaut")
                return self._load_default_model()
                
        except Exception as e:
            print(f"[ModelManager] Erreur lors du chargement depuis MLflow: {e}")
            print("[ModelManager] Utilisation du modèle par défaut")
            return self._load_default_model()
    
    def load_model_version(self, run_id: str, model_name: str = "embedding_model") -> SentenceTransformer:
        """
        Charge une version spécifique du modèle
        
        Args:
            run_id: ID du run MLflow
            model_name: Nom du modèle dans MLflow
            
        Returns:
            Modèle SentenceTransformer chargé
        """
        if run_id in self.model_cache:
            print(f"[ModelManager] Utilisation du modèle en cache (version: {run_id})")
            return self.model_cache[run_id]
        
        try:
            model_uri = f"runs:/{run_id}/{model_name}"
            print(f"[ModelManager] Chargement du modèle version {run_id}")
            
            model = mlflow.sentence_transformers.load_model(model_uri)
            self.model_cache[run_id] = model
            
            return model
        except Exception as e:
            print(f"[ModelManager] Erreur lors du chargement de la version {run_id}: {e}")
            return self._load_default_model()
    
    def _load_default_model(self) -> SentenceTransformer:
        """
        Charge le modèle par défaut (fallback)
        """
        if self.current_model is None:
            print("[ModelManager] Chargement du modèle par défaut")
            self.current_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        return self.current_model
    
    def get_model_info(self) -> Dict:
        """
        Retourne les informations sur le modèle actuel
        """
        return {
            "model_version": self.current_model_version or "default",
            "mlflow_tracking_uri": self.mlflow_tracking_uri,
            "cached_versions": list(self.model_cache.keys())
        }
    
    def predict_embedding(self, text: str, model_version: Optional[str] = None) -> np.ndarray:
        """
        Génère l'embedding d'un texte
        
        Args:
            text: Texte à encoder
            model_version: Version du modèle à utiliser (None = dernière version)
            
        Returns:
            Vecteur d'embedding
        """
        if model_version:
            model = self.load_model_version(model_version)
        else:
            if self.current_model is None:
                model = self.load_latest_model()
            else:
                model = self.current_model
        
        embedding = model.encode(
            [text],
            convert_to_numpy=True,
            normalize_embeddings=True
        )[0]
        
        return embedding
    
    def predict_similarity(self, text1: str, text2: str, model_version: Optional[str] = None) -> float:
        """
        Calcule la similarité cosinus entre deux textes
        
        Args:
            text1: Premier texte
            text2: Deuxième texte
            model_version: Version du modèle à utiliser
            
        Returns:
            Score de similarité (0-1)
        """
        emb1 = self.predict_embedding(text1, model_version)
        emb2 = self.predict_embedding(text2, model_version)
        
        similarity = np.dot(emb1, emb2)
        return float(similarity)

