# Projet MLOps - Talent Hunter NLP

Projet complet de MLOps avec Git, Docker, DVC, ZenML, MLflow, Optuna et déploiement API.

## 📋 Structure du Projet

```
.
├── api/                    # API FastAPI pour l'inférence
│   ├── main.py            # Endpoints API avec versioning
│   └── model_manager.py   # Gestionnaire de modèles MLflow
├── data/                   # Données (gérées par DVC)
│   ├── raw/               # Données brutes
│   └── processed/         # Données traitées
├── models/                 # Modèles entraînés
├── pipelines/              # Pipelines ZenML
│   ├── training_pipeline.py    # Pipeline d'entraînement
│   ├── optuna_optimization.py  # Optimisation hyperparamètres
│   └── run_pipeline.py          # Script d'exécution
├── src/                    # Code source du projet
├── scripts/                # Scripts utilitaires
├── docker-compose.yml      # Orchestration Docker
├── dockerfile              # Image Docker pour l'API
└── requirements.txt        # Dépendances Python
```

## 🚀 Installation et Configuration

### Prérequis

- Python 3.11+
- Docker et Docker Compose
- Git
- WSL Ubuntu (pour Windows)

### 1. Configuration Git

```bash
# Vérifier la configuration Git
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"

# Initialiser le dépôt (si pas déjà fait)
git init
git branch -M main
git checkout -b dev

# Créer les branches main et dev
git checkout -b main
git checkout -b dev
```

### 2. Installation des dépendances

```bash
# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Initialisation DVC

```bash
# Initialiser DVC
dvc init

# Ajouter les fichiers de données
dvc add data/raw/github_repos.csv
dvc add data/raw/github_users.csv
dvc add data/processed/profiles_enriched.csv
dvc add data/processed/profiles_embeddings.npy

# Configurer MinIO comme remote (après avoir lancé Docker)
dvc remote add -d minio s3://dvc-data --local
dvc remote modify minio endpointurl http://localhost:9000 --local
dvc remote modify minio access_key_id minioadmin --local
dvc remote modify minio secret_access_key minioadmin --local
```

### 4. Initialisation ZenML

```bash
# Initialiser ZenML
zenml init

# Configurer le store MLflow
zenml experiment-tracker register mlflow_tracker --flavor=mlflow \
    --tracking_uri=http://localhost:5000
```

## 🐳 Déploiement avec Docker

### Lancer tous les services

```bash
# Lancer MLflow, MinIO, PostgreSQL et l'API
docker-compose up -d

# Vérifier les services
docker-compose ps
```

### Accéder aux interfaces

- **API FastAPI**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs
- **MLflow UI**: http://localhost:5000
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

### Arrêter les services

```bash
docker-compose down
```

## 🔄 Pipeline ZenML

### Exécution simple (entraînement)

```bash
python pipelines/run_pipeline.py --mode train \
    --model-name "sentence-transformers/all-MiniLM-L6-v2" \
    --batch-size 32
```

### Optimisation avec Optuna

```bash
python pipelines/run_pipeline.py --mode optimize \
    --n-trials 10
```

### Exécution directe du pipeline

```python
from pipelines.training_pipeline import nlp_training_pipeline

pipeline_instance = nlp_training_pipeline(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    batch_size=32
)
metrics = pipeline_instance.run()
```

## 🌐 API Endpoints

### Endpoints disponibles

#### 1. `/predict` - Prédiction NLP
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Python developer with ML experience",
    "model_version": null
  }'
```

#### 2. `/predict/similarity` - Similarité entre textes
```bash
curl -X POST "http://localhost:8000/predict/similarity" \
  -H "Content-Type: application/json" \
  -d '{
    "text1": "Python developer",
    "text2": "Machine learning engineer",
    "model_version": null
  }'
```

#### 3. `/models/info` - Informations sur les modèles
```bash
curl http://localhost:8000/models/info
```

#### 4. `/models/load/{version}` - Charger une version spécifique
```bash
curl -X POST "http://localhost:8000/models/load/abc123def456"
```

#### 5. `/agent_search` - Recherche de talents (existant)
```bash
curl -X POST "http://localhost:8000/agent_search" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Looking for a Python developer",
    "top_k": 5
  }'
```

#### 6. `/health` - Vérification de santé
```bash
curl http://localhost:8000/health
```

## 📊 MLflow Tracking

### Accéder à MLflow

1. Ouvrir http://localhost:5000
2. Voir les expériences et runs
3. Comparer les métriques (Accuracy, MAE, etc.)
4. Télécharger les modèles versionnés

### Métriques trackées

- `mae`: Erreur moyenne absolue
- `accuracy`: Précision (%)
- `num_profiles`: Nombre de profils traités
- `embedding_dim`: Dimension des embeddings
- `avg_profile_length`: Longueur moyenne des profils

## 🔧 Versioning des Modèles

### Mise à jour v1 → v2

1. **Entraîner un nouveau modèle**:
   ```bash
   python pipelines/run_pipeline.py --mode train
   ```

2. **Le modèle est automatiquement enregistré dans MLflow** avec un nouveau run_id

3. **Charger la nouvelle version dans l'API**:
   ```bash
   # Option 1: Via l'endpoint API
   curl -X POST "http://localhost:8000/models/load/{nouveau_run_id}"
   
   # Option 2: Redémarrer l'API (charge automatiquement la dernière version)
   docker-compose restart nlp-api
   ```

4. **Utiliser une version spécifique**:
   ```bash
   curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Your text here",
       "model_version": "run_id_specifique"
     }'
   ```

## 📝 Workflow Complet

### 1. Développement (branche dev)

```bash
git checkout dev

# Faire des modifications
# Tester localement
python pipelines/run_pipeline.py --mode train

# Commit
git add .
git commit -m "Nouvelle fonctionnalité"
```

### 2. Entraînement et tracking

```bash
# Lancer le pipeline avec tracking MLflow
python pipelines/run_pipeline.py --mode train

# Ou optimiser les hyperparamètres
python pipelines/run_pipeline.py --mode optimize --n-trials 20
```

### 3. Versioning des données

```bash
# Ajouter de nouvelles données
dvc add data/raw/nouvelles_donnees.csv

# Push vers le remote
dvc push
```

### 4. Déploiement

```bash
# Merge vers main
git checkout main
git merge dev

# Build et déploiement Docker
docker-compose build
docker-compose up -d
```

## 🧪 Tests

### Tester l'API

```bash
# Test de santé
curl http://localhost:8000/health

# Test de prédiction
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "test"}'
```

### Tester le pipeline

```bash
python pipelines/run_pipeline.py --mode train
```

## 📚 Documentation Additionnelle

- [Guide DVC](README_DVC.md) - Versioning des données
- [Documentation MLflow](https://mlflow.org/docs/latest/index.html)
- [Documentation ZenML](https://docs.zenml.io/)
- [Documentation FastAPI](https://fastapi.tiangolo.com/)

## 🐛 Dépannage

### MLflow ne démarre pas

```bash
# Vérifier les logs
docker-compose logs mlflow

# Redémarrer les services
docker-compose restart mlflow postgres
```

### Erreur de connexion à MinIO

```bash
# Vérifier que MinIO est démarré
docker-compose ps minio

# Vérifier les credentials dans docker-compose.yml
```

### Modèle non trouvé dans MLflow

- Vérifier que le pipeline a bien été exécuté
- Vérifier l'URI MLflow dans les variables d'environnement
- Consulter les logs: `docker-compose logs mlflow`

## 📄 Licence

Ce projet est un projet académique pour le cours MLOps.

