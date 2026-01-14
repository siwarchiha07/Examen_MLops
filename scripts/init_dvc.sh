#!/bin/bash
# Script d'initialisation de DVC

echo "=== Initialisation de DVC ==="

# Initialiser DVC si ce n'est pas déjà fait
if [ ! -d ".dvc" ]; then
    echo "Initialisation de DVC..."
    dvc init
fi

# Ajouter les fichiers de données au tracking DVC
echo "Ajout des fichiers de données au tracking DVC..."

# Données brutes
if [ -f "data/raw/github_repos.csv" ]; then
    dvc add data/raw/github_repos.csv
fi

if [ -f "data/raw/github_users.csv" ]; then
    dvc add data/raw/github_users.csv
fi

# Données traitées
if [ -f "data/processed/profiles_enriched.csv" ]; then
    dvc add data/processed/profiles_enriched.csv
fi

if [ -f "data/processed/profiles_embeddings.npy" ]; then
    dvc add data/processed/profiles_embeddings.npy
fi

if [ -f "data/processed/profiles_index.csv" ]; then
    dvc add data/processed/profiles_index.csv
fi

echo "=== Configuration du remote MinIO (optionnel) ==="
echo "Pour configurer MinIO comme remote DVC, exécutez:"
echo "dvc remote add -d minio s3://dvc-data --local"
echo "dvc remote modify minio endpointurl http://localhost:9000 --local"
echo "dvc remote modify minio access_key_id minioadmin --local"
echo "dvc remote modify minio secret_access_key minioadmin --local"

echo "=== DVC initialisé avec succès ==="

