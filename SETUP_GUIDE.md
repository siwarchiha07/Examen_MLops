# 📖 Guide de Configuration Complète

Ce guide détaille chaque étape de configuration du projet MLOps.

## Étape 1 : Préparation et Gestion du Code (Git)

### 1.1 Configuration locale Git

```bash
# Vérifier la configuration actuelle
git config --global user.name
git config --global user.email

# Configurer si nécessaire
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"
```

### 1.2 Initialisation du dépôt

```bash
# Initialiser Git (si pas déjà fait)
git init

# Créer les branches main et dev
git checkout -b main
git checkout -b dev

# Ou utiliser le script
# Windows: .\scripts\init_git.bat
# Linux/Mac: ./scripts/init_git.sh
```

### 1.3 Structure du dépôt

Votre projet doit avoir :
- ✅ Branche `main` (stable, production)
- ✅ Branche `dev` (développement)
- ✅ Fichier `.gitignore` (déjà créé)

### 1.4 Workflow Git recommandé

```bash
# Travailler sur dev
git checkout dev

# Faire vos modifications
# ...

# Commit
git add .
git commit -m "Description des changements"

# Quand prêt pour production
git checkout main
git merge dev
git push origin main
```

## Étape 2 : Environnement et Conteneurisation (Docker)

### 2.1 Installation Docker

**Windows avec WSL Ubuntu:**

```bash
# Dans WSL Ubuntu
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Vérifier l'installation
docker --version
docker-compose --version
```

### 2.2 Structure Docker

Le projet contient :
- `dockerfile` : Image pour l'API FastAPI
- `docker-compose.yml` : Orchestration de tous les services

### 2.3 Services Docker

Le `docker-compose.yml` lance :
1. **PostgreSQL** : Base de données pour MLflow
2. **MinIO** : Stockage S3-compatible pour artifacts
3. **MLflow** : Serveur de tracking
4. **nlp-api** : API FastAPI pour l'inférence

### 2.4 Commandes Docker

```bash
# Lancer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down

# Rebuild après modification du code
docker-compose build
docker-compose up -d
```

## Étape 3 : Versioning des Données (DVC)

### 3.1 Installation DVC

```bash
pip install dvc dvc-s3
```

### 3.2 Initialisation DVC

```bash
# Initialiser DVC dans le projet
dvc init

# Ajouter les fichiers de données
dvc add data/raw/github_repos.csv
dvc add data/raw/github_users.csv
dvc add data/processed/profiles_enriched.csv
dvc add data/processed/profiles_embeddings.npy
```

### 3.3 Configuration Remote (MinIO)

Une fois MinIO lancé via Docker :

```bash
# Ajouter MinIO comme remote
dvc remote add -d minio s3://dvc-data --local

# Configurer l'endpoint
dvc remote modify minio endpointurl http://localhost:9000 --local

# Configurer les credentials
dvc remote modify minio access_key_id minioadmin --local
dvc remote modify minio secret_access_key minioadmin --local
```

### 3.4 Utilisation DVC

```bash
# Push des données vers le remote
dvc push

# Pull des données depuis le remote
dvc pull

# Voir les fichiers trackés
dvc list .

# Voir le statut
dvc status
```

## Étape 4 : Pipeline et Tracking (ZenML & MLflow)

### 4.1 Installation ZenML

```bash
pip install zenml[mlflow] zenml[server]
```

### 4.2 Initialisation ZenML

```bash
# Initialiser ZenML
zenml init

# Configurer le tracker MLflow
zenml experiment-tracker register mlflow_tracker --flavor=mlflow \
    --tracking_uri=http://localhost:5000
```

### 4.3 Structure du Pipeline

Le pipeline ZenML (`pipelines/training_pipeline.py`) contient 4 étapes :

1. **`load_data()`** : Chargement des données brutes
2. **`preprocess_data()`** : Prétraitement et enrichissement
3. **`train_model()`** : Génération des embeddings
4. **`evaluate_model()`** : Calcul des métriques

### 4.4 Exécution du Pipeline

```bash
# Mode simple (entraînement)
python pipelines/run_pipeline.py --mode train

# Mode optimisation (Optuna)
python pipelines/run_pipeline.py --mode optimize --n-trials 10
```

### 4.5 Tracking MLflow

MLflow track automatiquement :
- **Paramètres** : model_name, batch_size, etc.
- **Métriques** : MAE, Accuracy, etc.
- **Modèles** : Modèles versionnés sauvegardés

Accéder à MLflow UI : http://localhost:5000

## Étape 5 : Optimisation (Optuna)

### 5.1 Fonctionnement

Optuna teste automatiquement différents hyperparamètres :
- Modèles d'embedding (all-MiniLM-L6-v2, all-mpnet-base-v2, etc.)
- Tailles de batch (16, 32, 64)

### 5.2 Exécution

```bash
python pipelines/run_pipeline.py --mode optimize --n-trials 20
```

### 5.3 Résultats

Les meilleurs paramètres sont :
- Loggés dans MLflow
- Accessibles via `study.best_params`

## Étape 6 : Déploiement et Inférence

### 6.1 API Endpoints

L'API FastAPI expose plusieurs endpoints :

#### `/predict` - Prédiction NLP
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "Python developer", "model_version": null}'
```

#### `/predict/similarity` - Similarité
```bash
curl -X POST "http://localhost:8000/predict/similarity" \
  -H "Content-Type: application/json" \
  -d '{
    "text1": "Python developer",
    "text2": "ML engineer"
  }'
```

#### `/models/info` - Informations modèles
```bash
curl http://localhost:8000/models/info
```

#### `/models/load/{version}` - Charger une version
```bash
curl -X POST "http://localhost:8000/models/load/abc123"
```

### 6.2 Versioning des Modèles

#### Mise à jour v1 → v2

1. **Entraîner un nouveau modèle** :
   ```bash
   python pipelines/run_pipeline.py --mode train
   ```

2. **Le modèle est automatiquement enregistré dans MLflow** avec un nouveau run_id

3. **Charger la nouvelle version** :
   ```bash
   # Via API
   curl -X POST "http://localhost:8000/models/load/{nouveau_run_id}"
   
   # Ou redémarrer l'API (charge automatiquement la dernière version)
   docker-compose restart nlp-api
   ```

4. **Utiliser une version spécifique** :
   ```bash
   curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Your text",
       "model_version": "run_id_specifique"
     }'
   ```

### 6.3 Mise à jour sans interruption

L'API supporte le changement de version sans redémarrage :
- Charger une nouvelle version via `/models/load/{version}`
- Spécifier une version dans les requêtes `/predict`
- L'ancienne version reste disponible en cache

## ✅ Checklist de Configuration

- [ ] Git configuré avec nom et email
- [ ] Branches main et dev créées
- [ ] `.gitignore` vérifié
- [ ] Docker et Docker Compose installés
- [ ] Services Docker lancés (`docker-compose up -d`)
- [ ] DVC initialisé (`dvc init`)
- [ ] Données ajoutées à DVC (`dvc add`)
- [ ] Remote DVC configuré (MinIO)
- [ ] ZenML initialisé (`zenml init`)
- [ ] MLflow tracker configuré
- [ ] Pipeline testé (`python pipelines/run_pipeline.py --mode train`)
- [ ] API accessible (http://localhost:8000/docs)
- [ ] MLflow UI accessible (http://localhost:5000)

## 🎯 Prochaines Étapes

1. Ajouter vos propres données dans `data/raw/`
2. Exécuter le pipeline avec vos données
3. Optimiser les hyperparamètres avec Optuna
4. Déployer l'API en production
5. Mettre en place CI/CD (GitHub Actions, GitLab CI, etc.)

## 📚 Ressources

- [Documentation Git](https://git-scm.com/doc)
- [Documentation Docker](https://docs.docker.com/)
- [Documentation DVC](https://dvc.org/doc)
- [Documentation ZenML](https://docs.zenml.io/)
- [Documentation MLflow](https://mlflow.org/docs/latest/index.html)
- [Documentation Optuna](https://optuna.org/)

