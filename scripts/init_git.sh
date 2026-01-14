#!/bin/bash
# Script d'initialisation Git pour le projet MLOps

echo "=== Initialisation Git ==="

# Vérifier si Git est déjà initialisé
if [ -d ".git" ]; then
    echo "Git est déjà initialisé"
else
    echo "Initialisation du dépôt Git..."
    git init
fi

# Créer les branches main et dev si elles n'existent pas
if ! git show-ref --verify --quiet refs/heads/main; then
    echo "Création de la branche main..."
    git checkout -b main
fi

if ! git show-ref --verify --quiet refs/heads/dev; then
    echo "Création de la branche dev..."
    git checkout -b dev
fi

# Retourner sur dev pour le développement
git checkout dev

echo "=== Configuration Git terminée ==="
echo "Branches disponibles:"
git branch -a

echo ""
echo "Pour commencer à travailler:"
echo "  git checkout dev"
echo "  # Faire vos modifications"
echo "  git add ."
echo "  git commit -m 'Votre message'"
echo "  git checkout main"
echo "  git merge dev"

