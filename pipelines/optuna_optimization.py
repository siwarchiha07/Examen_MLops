"""
Pipeline d'optimisation des hyperparamètres avec Optuna
"""
import os
import sys
import optuna
from typing import Dict
from pipelines.training_pipeline import nlp_training_pipeline
import mlflow

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def objective(trial: optuna.Trial) -> float:
    """
    Fonction objectif pour Optuna
    """
    # Hyperparamètres à optimiser
    model_name = trial.suggest_categorical(
        "model_name",
        [
            "sentence-transformers/all-MiniLM-L6-v2",
            "sentence-transformers/all-mpnet-base-v2",
            "sentence-transformers/paraphrase-MiniLM-L6-v2"
        ]
    )
    
    batch_size = trial.suggest_categorical("batch_size", [16, 32, 64])
    
    # Log des paramètres dans MLflow
    with mlflow.start_run(nested=True):
        mlflow.log_params({
            "model_name": model_name,
            "batch_size": batch_size,
            "trial_number": trial.number
        })
        
        # Exécution du pipeline avec ces hyperparamètres
        pipeline_instance = nlp_training_pipeline(
            model_name=model_name,
            batch_size=batch_size
        )
        
        metrics = pipeline_instance.run()
        
        # La métrique à optimiser (on maximise l'accuracy ou minimise la MAE)
        if "accuracy" in metrics:
            score = metrics["accuracy"]
        elif "mae" in metrics:
            # On retourne l'inverse de la MAE pour maximiser
            score = -metrics["mae"]
        else:
            # Métrique par défaut
            score = metrics.get("num_profiles", 0)
        
        mlflow.log_metric("objective_score", score)
        
        return score


def optimize_hyperparameters(n_trials: int = 10) -> optuna.Study:
    """
    Lance l'optimisation des hyperparamètres avec Optuna
    """
    print(f"[OPTUNA] Début de l'optimisation avec {n_trials} essais...")
    
    # Création de l'étude Optuna
    study = optuna.create_study(
        direction="maximize",  # On maximise l'accuracy
        study_name="nlp_model_optimization"
    )
    
    # Lancement de l'optimisation
    study.optimize(objective, n_trials=n_trials)
    
    print("\n[OPTUNA] Optimisation terminée!")
    print(f"[OPTUNA] Meilleurs paramètres: {study.best_params}")
    print(f"[OPTUNA] Meilleur score: {study.best_value}")
    
    # Log des meilleurs paramètres dans MLflow
    with mlflow.start_run(run_name="optuna_best"):
        mlflow.log_params(study.best_params)
        mlflow.log_metric("best_score", study.best_value)
    
    return study


if __name__ == "__main__":
    # Exécution de l'optimisation
    study = optimize_hyperparameters(n_trials=10)

