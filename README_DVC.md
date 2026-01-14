# Guide DVC - Versioning des Données

## Installation

```bash
pip install dvc dvc-s3
```

## Initialisation

```bash
# Initialiser DVC dans le projet
dvc init

# Ajouter les fichiers de données
dvc add data/raw/github_repos.csv
dvc add data/raw/github_users.csv
dvc add data/processed/profiles_enriched.csv
dvc add data/processed/profiles_embeddings.npy
dvc add data/processed/profiles_index.csv
```

## Configuration avec MinIO (Remote Storage)

Une fois MinIO lancé via docker-compose, configurez DVC pour utiliser MinIO :

```bash
# Ajouter le remote MinIO
dvc remote add -d minio s3://dvc-data --local

# Configurer l'endpoint MinIO
dvc remote modify minio endpointurl http://localhost:9000 --local

# Configurer les credentials
dvc remote modify minio access_key_id minioadmin --local
dvc remote modify minio secret_access_key minioadmin --local
```

## Utilisation

### Push des données vers le remote
```bash
dvc push
```

### Pull des données depuis le remote
```bash
dvc pull
```

### Voir les fichiers trackés
```bash
dvc list .
```

### Voir le statut
```bash
dvc status
```

## Notes

- Les fichiers `.dvc` doivent être commités dans Git
- Les fichiers de données eux-mêmes sont stockés dans MinIO (ou un autre remote)
- Ne jamais commit les gros fichiers directement dans Git

