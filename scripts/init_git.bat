@echo off
REM Script d'initialisation Git pour Windows

echo === Initialisation Git ===

REM Vérifier si Git est déjà initialisé
if exist ".git" (
    echo Git est deja initialise
) else (
    echo Initialisation du depot Git...
    git init
)

REM Créer la branche main si elle n'existe pas
git show-ref --verify --quiet refs/heads/main
if errorlevel 1 (
    echo Creation de la branche main...
    git checkout -b main
)

REM Créer la branche dev si elle n'existe pas
git show-ref --verify --quiet refs/heads/dev
if errorlevel 1 (
    echo Creation de la branche dev...
    git checkout -b dev
)

REM Retourner sur dev pour le développement
git checkout dev

echo === Configuration Git terminee ===
echo Branches disponibles:
git branch -a

echo.
echo Pour commencer a travailler:
echo   git checkout dev
echo   # Faire vos modifications
echo   git add .
echo   git commit -m "Votre message"
echo   git checkout main
echo   git merge dev

