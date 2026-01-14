"""
Script pour exécuter le pipeline ZenML
"""
import os
import sys
from zenml import Client
from pipelines.training_pipeline import nlp_training_pipeline
from pipelines.optuna_optimization import optimize_hyperparameters

# Configuration de MLflow
os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5000"

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Exécuter le pipeline NLP")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["train", "optimize"],
        default="train",
        help="Mode d'exécution: train (entraînement simple) ou optimize (optimisation Optuna)"
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Nom du modèle à utiliser"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Taille du batch pour l'encodage"
    )
    parser.add_argument(
        "--n-trials",
        type=int,
        default=10,
        help="Nombre d'essais pour Optuna (mode optimize uniquement)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "train":
        print("[PIPELINE] Mode: Entraînement simple")
        pipeline_instance = nlp_training_pipeline(
            model_name=args.model_name,
            batch_size=args.batch_size
        )
        metrics = pipeline_instance.run()
        print(f"[PIPELINE] Métriques finales: {metrics}")
        
    elif args.mode == "optimize":
        print("[PIPELINE] Mode: Optimisation Optuna")
        study = optimize_hyperparameters(n_trials=args.n_trials)
        print(f"[PIPELINE] Meilleurs paramètres: {study.best_params}")

