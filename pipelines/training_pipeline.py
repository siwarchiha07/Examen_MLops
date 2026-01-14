"""
Pipeline ZenML pour l'entraînement du modèle NLP
Étapes : Chargement ➡️ Prétraitement ➡️ Entraînement ➡️ Évaluation
"""
import os
import sys
import pandas as pd
import numpy as np
from typing import Tuple, Dict
from sentence_transformers import SentenceTransformer
from sklearn.metrics import mean_absolute_error
import mlflow
import mlflow.sentence_transformers
from zenml import step, pipeline
from zenml.integrations.mlflow.mlflow_step_decorator import enable_mlflow

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@step(enable_cache=False)
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Étape 1 : Chargement des données brutes
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    users_path = os.path.join(base_dir, "data", "raw", "github_users.csv")
    repos_path = os.path.join(base_dir, "data", "raw", "github_repos.csv")
    
    print(f"[STEP: Load] Lecture utilisateurs : {users_path}")
    users_df = pd.read_csv(users_path)
    
    print(f"[STEP: Load] Lecture repos : {repos_path}")
    repos_df = pd.read_csv(repos_path)
    
    print(f"[STEP: Load] {len(users_df)} utilisateurs, {len(repos_df)} repos chargés")
    
    return users_df, repos_df


@step(enable_cache=False)
def preprocess_data(users_df: pd.DataFrame, repos_df: pd.DataFrame) -> pd.DataFrame:
    """
    Étape 2 : Prétraitement et enrichissement des données
    """
    print("[STEP: Preprocess] Début du prétraitement...")
    
    # Nettoyage des utilisateurs
    users_cols = [
        "login", "name", "company", "location", "bio",
        "followers", "public_repos", "public_gists"
    ]
    users_df = users_df[[c for c in users_cols if c in users_df.columns]].copy()
    users_df = users_df.fillna("")
    
    # Agrégation des repos par utilisateur
    repos_df["description"] = repos_df["description"].fillna("")
    repos_df["language"] = repos_df["language"].fillna("")
    repos_df["stargazers_count"] = pd.to_numeric(
        repos_df.get("stargazers_count", 0), errors="coerce"
    ).fillna(0)
    
    # Texte concaténé des descriptions
    agg_desc = repos_df.groupby("owner_login")["description"].apply(
        lambda x: " . ".join([d for d in x if isinstance(d, str) and d.strip() != ""])
    )
    
    # Liste des langages
    agg_lang = repos_df.groupby("owner_login")["language"].apply(
        lambda x: ", ".join(sorted(set([l for l in x if isinstance(l, str) and l.strip() != ""])))
    )
    
    # Total de stars et nombre de repos
    agg_stars = repos_df.groupby("owner_login")["stargazers_count"].sum()
    agg_nb_repos = repos_df.groupby("owner_login")["repo_name"].count()
    
    repos_agg_df = pd.DataFrame({
        "login": agg_desc.index,
        "repos_descriptions": agg_desc.values,
        "languages_list": agg_lang.reindex(agg_desc.index).fillna(""),
        "total_stars": agg_stars.reindex(agg_desc.index).fillna(0).astype(int),
        "nb_repos_fetched": agg_nb_repos.reindex(agg_desc.index).fillna(0).astype(int),
    })
    
    # Fusion users + repos
    merged_df = pd.merge(
        users_df,
        repos_agg_df,
        on="login",
        how="inner",
    )
    
    # Construction du texte profil
    def build_profile_text(row):
        parts = []
        if row.get("name"):
            parts.append(str(row["name"]))
        if row.get("bio"):
            parts.append(str(row["bio"]))
        if row.get("company"):
            parts.append(f"Company: {row['company']}")
        if row.get("location"):
            parts.append(f"Location: {row['location']}")
        if row.get("languages_list"):
            parts.append(f"Languages: {row['languages_list']}")
        if row.get("nb_repos_fetched", 0) > 0:
            parts.append(f"Number of repositories: {row['nb_repos_fetched']}")
        if row.get("total_stars", 0) > 0:
            parts.append(f"Total stars: {row['total_stars']}")
        if row.get("repos_descriptions"):
            parts.append(f"Projects: {row['repos_descriptions']}")
        
        text = " . ".join([p for p in parts if isinstance(p, str) and p.strip() != ""])
        return text
    
    merged_df["profile_text"] = merged_df.apply(build_profile_text, axis=1)
    merged_df = merged_df[merged_df["profile_text"].str.strip() != ""].copy()
    merged_df["total_stars"] = pd.to_numeric(merged_df["total_stars"], errors="coerce").fillna(0).astype(int)
    merged_df = merged_df.sort_values("total_stars", ascending=False)
    
    print(f"[STEP: Preprocess] {len(merged_df)} profils enrichis créés")
    
    return merged_df


@step(enable_cache=False)
@enable_mlflow
def train_model(
    processed_df: pd.DataFrame,
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    batch_size: int = 32
) -> Tuple[SentenceTransformer, np.ndarray]:
    """
    Étape 3 : Entraînement (génération des embeddings)
    """
    print(f"[STEP: Train] Chargement du modèle : {model_name}")
    
    # Log des hyperparamètres dans MLflow
    mlflow.log_param("model_name", model_name)
    mlflow.log_param("batch_size", batch_size)
    mlflow.log_param("num_profiles", len(processed_df))
    
    # Chargement du modèle
    model = SentenceTransformer(model_name)
    
    # Génération des embeddings
    texts = processed_df["profile_text"].astype(str).tolist()
    print(f"[STEP: Train] Encodage de {len(texts)} profils...")
    
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    
    print(f"[STEP: Train] Embeddings générés : shape {embeddings.shape}")
    
    # Log du modèle dans MLflow
    mlflow.sentence_transformers.log_model(model, "embedding_model")
    
    return model, embeddings


@step(enable_cache=False)
@enable_mlflow
def evaluate_model(
    processed_df: pd.DataFrame,
    embeddings: np.ndarray,
    model: SentenceTransformer
) -> Dict[str, float]:
    """
    Étape 4 : Évaluation du modèle
    """
    print("[STEP: Evaluate] Début de l'évaluation...")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gold_path = os.path.join(base_dir, "data", "processed", "gold_standard.csv")
    
    metrics = {}
    
    # Si un fichier gold standard existe, on calcule les métriques
    if os.path.exists(gold_path):
        try:
            gold_df = pd.read_csv(gold_path)
            gold_df.columns = [c.strip().lower() for c in gold_df.columns]
            results_df = processed_df.copy()
            results_df.columns = [c.strip().lower() for c in results_df.columns]
            
            comparison = pd.merge(gold_df, results_df, on="login", how="inner")
            
            if not comparison.empty and "agent_score" in comparison.columns:
                y_true_col = "note de pertinence (humain)"
                y_pred_col = "agent_score"
                
                if y_true_col in comparison.columns:
                    comparison[y_true_col] = pd.to_numeric(comparison[y_true_col], errors="coerce")
                    comparison[y_pred_col] = pd.to_numeric(comparison[y_pred_col], errors="coerce")
                    comparison = comparison.dropna(subset=[y_true_col, y_pred_col])
                    
                    if len(comparison) > 0:
                        y_true = comparison[y_true_col]
                        y_pred = comparison[y_pred_col]
                        
                        mae = mean_absolute_error(y_true, y_pred)
                        accuracy = np.mean(np.abs(y_true - y_pred) < 0.15) * 100
                        
                        metrics["mae"] = mae
                        metrics["accuracy"] = accuracy
                        
                        print(f"[STEP: Evaluate] MAE: {mae:.4f}, Accuracy: {accuracy:.2f}%")
        except Exception as e:
            print(f"[STEP: Evaluate] Erreur lors de l'évaluation: {e}")
    
    # Métriques de base sur les embeddings
    metrics["num_profiles"] = len(processed_df)
    metrics["embedding_dim"] = embeddings.shape[1]
    metrics["avg_profile_length"] = processed_df["profile_text"].str.len().mean()
    
    # Log des métriques dans MLflow
    for key, value in metrics.items():
        mlflow.log_metric(key, value)
    
    print(f"[STEP: Evaluate] Métriques calculées: {metrics}")
    
    return metrics


@pipeline(enable_cache=False)
def nlp_training_pipeline(
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    batch_size: int = 32
):
    """
    Pipeline complet d'entraînement NLP
    """
    # Chargement des données
    users_df, repos_df = load_data()
    
    # Prétraitement
    processed_df = preprocess_data(users_df, repos_df)
    
    # Entraînement
    model, embeddings = train_model(processed_df, model_name, batch_size)
    
    # Évaluation
    metrics = evaluate_model(processed_df, embeddings, model)
    
    return metrics


if __name__ == "__main__":
    # Exécution du pipeline
    pipeline_instance = nlp_training_pipeline(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        batch_size=32
    )
    pipeline_instance.run()

