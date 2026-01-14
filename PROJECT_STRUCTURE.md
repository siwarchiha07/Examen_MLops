# 📁 Structure du Projet MLOps

## Vue d'ensemble

Ce projet implémente un pipeline MLOps complet pour un système de recherche de talents basé sur NLP.

## Structure des dossiers

```
.
├── api/                          # API FastAPI pour l'inférence
│   ├── __init__.py
│   ├── main.py                   # Endpoints API avec versioning des modèles
│   └── model_manager.py          # Gestionnaire de modèles MLflow
│
├── data/                         # Données (gérées par DVC)
│   ├── .gitkeep
│   ├── raw/                      # Données brutes
│   │   ├── github_repos.csv
│   │   └── github_users.csv
│   └── processed/                # Données traitées
│       ├── profiles_enriched.csv
│       ├── profiles_embeddings.npy
│       └── profiles_index.csv
│
├── models/                       # Modèles entraînés
│   └── .gitkeep
│
├── notebooks/                    # Notebooks Jupyter (optionnel)
│
├── pipelines/                    # Pipelines ZenML
│   ├── __init__.py
│   ├── training_pipeline.py      # Pipeline principal (4 étapes)
│   ├── optuna_optimization.py    # Optimisation hyperparamètres
│   └── run_pipeline.py           # Script d'exécution
│
├── scripts/                      # Scripts utilitaires
│   ├── init_dvc.sh              # Initialisation DVC (Linux/Mac)
│   ├── init_dvc.bat             # Initialisation DVC (Windows)
│   ├── init_git.sh              # Initialisation Git (Linux/Mac)
│   └── init_git.bat             # Initialisation Git (Windows)
│
├── src/                          # Code source du projet
│   ├── __init__.py
│   ├── agent.py                 # Fonctions d'analyse IA
│   ├── build_profiles.py        # Construction des profils
│   ├── config.py                # Configuration
│   ├── embedding.py             # Génération d'embeddings
│   ├── eval_metrics.py          # Métriques d'évaluation
│   ├── matching.py              # Recherche de talents
│   └── scraping_github.py       # Scraping GitHub
│
├── .dvc/                         # Configuration DVC (généré)
│   └── config                   # Config remote MinIO
│
├── .gitignore                    # Fichiers ignorés par Git
├── docker-compose.yml            # Orchestration Docker
├── dockerfile                    # Image Docker pour l'API
├── requirements.txt              # Dépendances Python
│
├── README.md                     # Documentation principale
├── QUICKSTART.md                 # Guide de démarrage rapide
├── SETUP_GUIDE.md                # Guide de configuration détaillé
├── README_DVC.md                 # Guide DVC
└── PROJECT_STRUCTURE.md          # Ce fichier
```

## Flux de données

```
Données brutes (CSV)
    ↓
[DVC] Versioning
    ↓
Pipeline ZenML
    ├── Étape 1: Chargement
    ├── Étape 2: Prétraitement
    ├── Étape 3: Entraînement
    └── Étape 4: Évaluation
    ↓
[MLflow] Tracking
    ├── Métriques (MAE, Accuracy)
    ├── Paramètres (model_name, batch_size)
    └── Modèles versionnés
    ↓
API FastAPI
    ├── /predict
    ├── /predict/similarity
    └── /models/load/{version}
```

## Technologies utilisées

### Versioning
- **Git** : Versioning du code
- **DVC** : Versioning des données

### Conteneurisation
- **Docker** : Conteneurisation de l'API
- **Docker Compose** : Orchestration des services

### MLOps
- **ZenML** : Pipeline orchestré
- **MLflow** : Tracking des expériences
- **Optuna** : Optimisation des hyperparamètres

### API
- **FastAPI** : Framework API moderne
- **Uvicorn** : Serveur ASGI

### NLP
- **Sentence Transformers** : Modèles d'embedding
- **scikit-learn** : Métriques d'évaluation

## Services Docker

| Service | Port | Description |
|---------|------|-------------|
| nlp-api | 8000 | API FastAPI |
| mlflow | 5000 | Serveur MLflow |
| minio | 9000, 9001 | Stockage S3-compatible |
| postgres | 5432 | Base de données MLflow |

## Endpoints API

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Statut de l'API |
| `/health` | GET | Vérification de santé |
| `/predict` | POST | Prédiction NLP |
| `/predict/similarity` | POST | Similarité entre textes |
| `/models/info` | GET | Informations sur les modèles |
| `/models/load/{version}` | POST | Charger une version |
| `/agent_search` | POST | Recherche de talents |

## Fichiers de configuration

- `.gitignore` : Exclut les fichiers volumineux de Git
- `.dvc/config` : Configuration du remote DVC (MinIO)
- `docker-compose.yml` : Configuration des services Docker
- `requirements.txt` : Dépendances Python

## Workflow recommandé

1. **Développement** (branche `dev`)
   - Modifier le code
   - Tester localement
   - Commit sur `dev`

2. **Entraînement**
   - Exécuter le pipeline ZenML
   - Tracking automatique dans MLflow
   - Optimisation avec Optuna (optionnel)

3. **Versioning**
   - Ajouter nouvelles données avec DVC
   - Push vers remote MinIO

4. **Déploiement** (branche `main`)
   - Merge `dev` → `main`
   - Build Docker
   - Déploiement production

5. **Mise à jour modèle**
   - Entraîner nouveau modèle
   - Charger via API `/models/load/{version}`
   - Pas besoin de redémarrer l'API

## Notes importantes

- Les données volumineuses sont gérées par DVC, pas Git
- Les modèles sont versionnés dans MLflow
- L'API supporte le changement de version sans redémarrage
- Tous les services sont orchestrés via Docker Compose

