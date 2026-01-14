# 🚀 Guide de Démarrage Rapide

Ce guide vous permet de démarrer rapidement le projet MLOps.

## ⚡ Démarrage en 5 minutes

### 1. Configuration Git (2 min)

```bash
# Windows (PowerShell)
.\scripts\init_git.bat

# Linux/Mac
chmod +x scripts/init_git.sh
./scripts/init_git.sh
```

### 2. Installation des dépendances (2 min)

```bash
# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Lancer Docker (1 min)

```bash
# Démarrer tous les services (MLflow, MinIO, PostgreSQL, API)
docker-compose up -d

# Vérifier que tout fonctionne
docker-compose ps
```

### 4. Accéder aux interfaces

- **API**: http://localhost:8000/docs
- **MLflow**: http://localhost:5000
- **MinIO**: http://localhost:9001 (minioadmin/minioadmin)

## 📝 Prochaines étapes

### Initialiser DVC

```bash
# Initialiser DVC
dvc init

# Ajouter vos données
dvc add data/raw/github_repos.csv
dvc add data/raw/github_users.csv
```

### Exécuter le pipeline

```bash
# Entraînement simple
python pipelines/run_pipeline.py --mode train

# Optimisation avec Optuna
python pipelines/run_pipeline.py --mode optimize --n-trials 10
```

### Tester l'API

```bash
# Test de santé
curl http://localhost:8000/health

# Test de prédiction
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "Python developer"}'
```

## 🔧 Commandes utiles

### Docker

```bash
# Voir les logs
docker-compose logs -f nlp-api
docker-compose logs -f mlflow

# Redémarrer un service
docker-compose restart nlp-api

# Arrêter tous les services
docker-compose down
```

### Git

```bash
# Travailler sur dev
git checkout dev

# Commit
git add .
git commit -m "Description des changements"

# Merge vers main
git checkout main
git merge dev
```

### DVC

```bash
# Voir les fichiers trackés
dvc list .

# Push vers le remote
dvc push

# Pull depuis le remote
dvc pull
```

## ❓ Problèmes courants

### Port déjà utilisé

```bash
# Changer les ports dans docker-compose.yml
# Par exemple, changer 8000:8000 en 8001:8000
```

### MLflow ne démarre pas

```bash
# Vérifier les logs
docker-compose logs mlflow

# Redémarrer PostgreSQL et MLflow
docker-compose restart postgres mlflow
```

### Erreur d'import ZenML

```bash
# Réinstaller ZenML
pip install --upgrade zenml[mlflow]
```

## 📚 Documentation complète

Consultez [README.md](README.md) pour la documentation complète.

