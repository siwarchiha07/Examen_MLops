# 📋 Liste des Commandes à Exécuter

Ce document liste toutes les commandes à exécuter pour mettre en place le projet MLOps, étape par étape.

## 🔧 Étape 1 : Configuration Git

### Windows (PowerShell)
```powershell
# Vérifier la configuration Git
git config --global user.name
git config --global user.email

# Configurer si nécessaire
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"

# Initialiser Git et créer les branches
.\scripts\init_git.bat
```

### Linux/Mac (Bash)
```bash
# Vérifier la configuration Git
git config --global user.name
git config --global user.email

# Configurer si nécessaire
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"

# Rendre le script exécutable et l'exécuter
chmod +x scripts/init_git.sh
./scripts/init_git.sh
```

### Vérification
```bash
# Vérifier les branches créées
git branch -a
```

---

## 🐍 Étape 2 : Configuration de l'Environnement Python

### Windows
```powershell
# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement
.venv\Scripts\activate

# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt
```

### Linux/Mac
```bash
# Créer l'environnement virtuel
python3 -m venv .venv

# Activer l'environnement
source .venv/bin/activate

# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt
```

### Vérification
```bash
# Vérifier l'installation
pip list | grep -E "mlflow|zenml|dvc|optuna"
```

---

## 🐳 Étape 3 : Lancement des Services Docker

### Lancer tous les services
```bash
# Démarrer tous les services en arrière-plan
docker-compose up -d

# Vérifier que tous les services sont démarrés
docker-compose ps
```

### Vérifier les logs
```bash
# Voir les logs de tous les services
docker-compose logs -f

# Voir les logs d'un service spécifique
docker-compose logs -f mlflow
docker-compose logs -f nlp-api
docker-compose logs -f postgres
docker-compose logs -f minio
```

### Vérifier l'état des services
```bash
# Vérifier que les services sont en cours d'exécution
docker-compose ps

# Vérifier les ports utilisés
netstat -an | findstr "5000 8000 9000 9001"  # Windows
# ou
netstat -an | grep -E "5000|8000|9000|9001"  # Linux/Mac
```

### Accéder aux interfaces
- **API FastAPI** : http://localhost:8000/docs
- **MLflow UI** : http://localhost:5000
- **MinIO Console** : http://localhost:9001 (minioadmin/minioadmin)

---

## 📦 Étape 4 : Initialisation DVC

### Initialiser DVC
```bash
# Initialiser DVC dans le projet
dvc init

# Commit des fichiers DVC dans Git
git add .dvc .dvcignore
git commit -m "Initialize DVC"
```

### Ajouter les fichiers de données au tracking DVC

#### Windows
```powershell
# Utiliser le script automatique
.\scripts\init_dvc.bat

# Ou manuellement
dvc add data\raw\github_repos.csv
dvc add data\raw\github_users.csv
dvc add data\processed\profiles_enriched.csv
dvc add data\processed\profiles_embeddings.npy
dvc add data\processed\profiles_index.csv
```

#### Linux/Mac
```bash
# Utiliser le script automatique
chmod +x scripts/init_dvc.sh
./scripts/init_dvc.sh

# Ou manuellement
dvc add data/raw/github_repos.csv
dvc add data/raw/github_users.csv
dvc add data/processed/profiles_enriched.csv
dvc add data/processed/profiles_embeddings.npy
dvc add data/processed/profiles_index.csv
```

### Configurer le remote MinIO (après avoir lancé Docker)
```bash
# Ajouter MinIO comme remote DVC
dvc remote add -d minio s3://dvc-data --local

# Configurer l'endpoint MinIO
dvc remote modify minio endpointurl http://localhost:9000 --local

# Configurer les credentials
dvc remote modify minio access_key_id minioadmin --local
dvc remote modify minio secret_access_key minioadmin --local

# Vérifier la configuration
dvc remote list
```

### Utiliser DVC
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

---

## 🔬 Étape 5 : Initialisation ZenML

### Initialiser ZenML
```bash
# Initialiser ZenML
zenml init

# Vérifier l'initialisation
zenml status
```

### Configurer le tracker MLflow (optionnel)
```bash
# Enregistrer le tracker MLflow
zenml experiment-tracker register mlflow_tracker --flavor=mlflow \
    --tracking_uri=http://localhost:5000

# Vérifier les trackers enregistrés
zenml experiment-tracker list
```

---

## 🚀 Étape 6 : Exécution du Pipeline

### Mode simple (entraînement)
```bash
# Exécuter le pipeline en mode entraînement
python pipelines/run_pipeline.py --mode train \
    --model-name "sentence-transformers/all-MiniLM-L6-v2" \
    --batch-size 32
```

### Mode optimisation (Optuna)
```bash
# Exécuter le pipeline en mode optimisation
python pipelines/run_pipeline.py --mode optimize \
    --n-trials 10
```

### Exécution avec paramètres personnalisés
```bash
# Avec un modèle différent
python pipelines/run_pipeline.py --mode train \
    --model-name "sentence-transformers/all-mpnet-base-v2" \
    --batch-size 64

# Avec plus d'essais pour Optuna
python pipelines/run_pipeline.py --mode optimize \
    --n-trials 20
```

---

## 🌐 Étape 7 : Tester l'API

### Vérifier la santé de l'API
```bash
# Test de santé
curl http://localhost:8000/health

# Ou avec PowerShell (Windows)
Invoke-WebRequest -Uri http://localhost:8000/health
```

### Tester l'endpoint /predict
```bash
# Test de prédiction
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Python developer with ML experience\", \"model_version\": null}"

# Ou avec PowerShell (Windows)
$body = @{
    text = "Python developer with ML experience"
    model_version = $null
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/predict `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

### Tester l'endpoint /predict/similarity
```bash
# Test de similarité
curl -X POST "http://localhost:8000/predict/similarity" \
  -H "Content-Type: application/json" \
  -d "{\"text1\": \"Python developer\", \"text2\": \"Machine learning engineer\", \"model_version\": null}"
```

### Tester l'endpoint /models/info
```bash
# Informations sur les modèles
curl http://localhost:8000/models/info
```

### Tester l'endpoint /agent_search
```bash
# Recherche de talents
curl -X POST "http://localhost:8000/agent_search" \
  -H "Content-Type: application/json" \
  -d "{\"job_description\": \"Looking for a Python developer\", \"top_k\": 5}"
```

---

## 🔄 Étape 8 : Gestion des Versions de Modèles

### Charger une version spécifique
```bash
# Récupérer le run_id depuis MLflow UI (http://localhost:5000)
# Puis charger cette version
curl -X POST "http://localhost:8000/models/load/RUN_ID_ICI"
```

### Utiliser une version spécifique dans les prédictions
```bash
# Prédiction avec une version spécifique
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Your text\", \"model_version\": \"RUN_ID_ICI\"}"
```

---

## 📊 Étape 9 : Accéder à MLflow

### Ouvrir MLflow UI
```bash
# Ouvrir dans le navigateur
# Windows
start http://localhost:5000

# Linux
xdg-open http://localhost:5000

# Mac
open http://localhost:5000
```

### Vérifier les runs MLflow via API
```bash
# Lister les expériences
curl http://localhost:5000/api/2.0/mlflow/experiments/list
```

---

## 🛠️ Commandes de Maintenance

### Redémarrer un service Docker
```bash
# Redémarrer l'API
docker-compose restart nlp-api

# Redémarrer MLflow
docker-compose restart mlflow

# Redémarrer tous les services
docker-compose restart
```

### Rebuild après modification du code
```bash
# Rebuild l'image de l'API
docker-compose build nlp-api

# Redémarrer avec la nouvelle image
docker-compose up -d nlp-api
```

### Voir les logs en temps réel
```bash
# Logs de tous les services
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f nlp-api
```

### Arrêter les services
```bash
# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes (⚠️ supprime les données)
docker-compose down -v
```

---

## 🔍 Commandes de Vérification

### Vérifier l'installation Python
```bash
# Vérifier les packages installés
pip list

# Vérifier les versions spécifiques
pip show mlflow
pip show zenml
pip show dvc
pip show optuna
```

### Vérifier Docker
```bash
# Vérifier la version Docker
docker --version
docker-compose --version

# Vérifier les conteneurs en cours d'exécution
docker ps

# Vérifier les images
docker images
```

### Vérifier Git
```bash
# Vérifier les branches
git branch -a

# Vérifier le statut
git status

# Voir l'historique
git log --oneline
```

### Vérifier DVC
```bash
# Vérifier la configuration
dvc remote list

# Vérifier les fichiers trackés
dvc list .

# Vérifier le statut
dvc status
```

### Vérifier ZenML
```bash
# Vérifier le statut ZenML
zenml status

# Lister les composants
zenml experiment-tracker list
zenml artifact-store list
```

---

## 🚨 Dépannage

### Si MLflow ne démarre pas
```bash
# Vérifier les logs
docker-compose logs mlflow

# Vérifier que PostgreSQL est démarré
docker-compose ps postgres

# Redémarrer PostgreSQL puis MLflow
docker-compose restart postgres
docker-compose restart mlflow
```

### Si l'API ne répond pas
```bash
# Vérifier les logs
docker-compose logs nlp-api

# Vérifier que le conteneur est en cours d'exécution
docker-compose ps nlp-api

# Redémarrer l'API
docker-compose restart nlp-api
```

### Si les ports sont déjà utilisés
```bash
# Trouver le processus utilisant le port (Windows)
netstat -ano | findstr :8000
netstat -ano | findstr :5000

# Trouver le processus utilisant le port (Linux/Mac)
lsof -i :8000
lsof -i :5000

# Modifier les ports dans docker-compose.yml si nécessaire
```

### Réinstaller les dépendances
```bash
# Désactiver l'environnement virtuel
deactivate

# Supprimer l'environnement virtuel
rm -rf .venv  # Linux/Mac
rmdir /s .venv  # Windows

# Recréer et réinstaller
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

## 📝 Checklist Rapide

Exécutez ces commandes dans l'ordre :

```bash
# 1. Git
.\scripts\init_git.bat  # Windows
# ou
./scripts/init_git.sh   # Linux/Mac

# 2. Environnement Python
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 3. Docker
docker-compose up -d

# 4. DVC
dvc init
.\scripts\init_dvc.bat  # Windows
# ou
./scripts/init_dvc.sh   # Linux/Mac
dvc remote add -d minio s3://dvc-data --local
dvc remote modify minio endpointurl http://localhost:9000 --local
dvc remote modify minio access_key_id minioadmin --local
dvc remote modify minio secret_access_key minioadmin --local

# 5. ZenML
zenml init

# 6. Pipeline
python pipelines/run_pipeline.py --mode train

# 7. Tester l'API
curl http://localhost:8000/health
```

---

## 🎯 Commandes Essentielles (Résumé)

```bash
# Démarrage complet
docker-compose up -d
python pipelines/run_pipeline.py --mode train

# Vérification
curl http://localhost:8000/health
curl http://localhost:5000  # MLflow

# Arrêt
docker-compose down
```

