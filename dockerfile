# Image de base légère avec Python
FROM python:3.11-slim

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Dossier de travail dans le conteneur
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt api/requirements.txt* ./

# Installation des dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Créer les dossiers nécessaires
RUN mkdir -p /app/data/processed /app/models /app/mlruns

# Exposer le port 8000 pour FastAPI
EXPOSE 8000

# Variables d'environnement pour MLflow
ENV MLFLOW_TRACKING_URI=http://mlflow:5000
ENV MLFLOW_BACKEND_STORE_URI=postgresql://mlflow:mlflow@postgres:5432/mlflow
ENV MLFLOW_DEFAULT_ARTIFACT_ROOT=s3://mlflow-artifacts

# Lancer l'application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
