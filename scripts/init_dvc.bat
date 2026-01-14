@echo off
REM Script d'initialisation de DVC pour Windows

echo === Initialisation de DVC ===

REM Initialiser DVC si ce n'est pas déjà fait
if not exist ".dvc" (
    echo Initialisation de DVC...
    dvc init
)

REM Ajouter les fichiers de données au tracking DVC
echo Ajout des fichiers de données au tracking DVC...

REM Données brutes
if exist "data\raw\github_repos.csv" (
    dvc add data\raw\github_repos.csv
)

if exist "data\raw\github_users.csv" (
    dvc add data\raw\github_users.csv
)

REM Données traitées
if exist "data\processed\profiles_enriched.csv" (
    dvc add data\processed\profiles_enriched.csv
)

if exist "data\processed\profiles_embeddings.npy" (
    dvc add data\processed\profiles_embeddings.npy
)

if exist "data\processed\profiles_index.csv" (
    dvc add data\processed\profiles_index.csv
)

echo === Configuration du remote MinIO (optionnel) ===
echo Pour configurer MinIO comme remote DVC, executez:
echo dvc remote add -d minio s3://dvc-data --local
echo dvc remote modify minio endpointurl http://localhost:9000 --local
echo dvc remote modify minio access_key_id minioadmin --local
echo dvc remote modify minio secret_access_key minioadmin --local

echo === DVC initialise avec succes ===

