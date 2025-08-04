#!/bin/bash

# SAMA ÉTAT v1.3 Stable - Script de Release GitHub
# Ce script prépare et publie la version 1.3 stable sur GitHub

set -e  # Arrêter en cas d'erreur

echo "🚀 SAMA ÉTAT v1.3 Stable - Préparation Release GitHub"
echo "=================================================="

# Variables
VERSION="v1.3-stable"
BRANCH="main"
REPO_URL="https://github.com/loi200812/sama-etat.git"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher des messages colorés
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérification des prérequis
log_info "Vérification des prérequis..."

# Vérifier si Git est installé
if ! command -v git &> /dev/null; then
    log_error "Git n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier si nous sommes dans un repository Git
if [ ! -d ".git" ]; then
    log_warning "Pas de repository Git détecté. Initialisation..."
    git init
    git remote add origin $REPO_URL
    log_success "Repository Git initialisé"
fi

# Configuration Git (si pas déjà configuré)
if [ -z "$(git config user.name)" ]; then
    log_info "Configuration Git utilisateur..."
    git config user.name "SAMA ÉTAT Team"
    git config user.email "dev@sama-etat.sn"
    log_success "Configuration Git terminée"
fi

# Vérifier la branche actuelle
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
log_info "Branche actuelle: $CURRENT_BRANCH"

# Créer le fichier .gitignore si nécessaire
if [ ! -f ".gitignore" ]; then
    log_info "Création du fichier .gitignore..."
    cat > .gitignore << 'EOF'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Odoo specific
*.pyc
*.pyo
.DS_Store
.vscode/
.idea/

# Backup files
*.bak
*.backup
*~

# Log files
*.log

# Temporary files
*.tmp
*.temp
EOF
    log_success "Fichier .gitignore créé"
fi

# Mise à jour du fichier __manifest__.py avec la nouvelle version
log_info "Mise à jour de la version dans __manifest__.py..."
if [ -f "__manifest__.py" ]; then
    sed -i "s/'version': '[^']*'/'version': '1.3.0'/" __manifest__.py
    log_success "Version mise à jour dans __manifest__.py"
fi

# Créer un fichier VERSION
echo "1.3.0" > VERSION
log_success "Fichier VERSION créé"

# Ajouter tous les fichiers
log_info "Ajout des fichiers au repository..."
git add .

# Vérifier les changements
CHANGES=$(git diff --cached --name-only)
if [ -z "$CHANGES" ]; then
    log_warning "Aucun changement détecté. Vérification des fichiers non suivis..."
    git add -A
    CHANGES=$(git diff --cached --name-only)
fi

if [ ! -z "$CHANGES" ]; then
    log_success "Fichiers ajoutés:"
    echo "$CHANGES" | sed 's/^/  - /'
else
    log_warning "Aucun changement à commiter"
fi

# Commit des changements
log_info "Création du commit v1.3 stable..."
git commit -m "🚀 Release v1.3 Stable - Carte Interactive & Workflow Événements

✨ Nouvelles fonctionnalités:
- 🗺️ Carte interactive plein écran avec géolocalisation GPS
- 📅 Workflow complet des événements gouvernementaux
- 🔄 Création automatique d'événements Odoo lors de la validation
- 📱 Interface responsive et moderne

🐛 Corrections:
- Erreurs XML dans les vues corrigées
- Variables non définies (axis_url, pillar_url) résolues
- Optimisations performance carte

📚 Documentation:
- Guide d'installation v1.3 complet
- Changelog détaillé avec toutes les nouveautés
- Documentation des dépendances
- README mis à jour avec carte interactive

🛠️ Technologies:
- Leaflet 1.7.1 pour la cartographie
- MarkerCluster 1.4.1 pour le regroupement
- OpenStreetMap pour les tuiles
- Bootstrap 5 pour l'interface responsive

Une République Transparente, Projet par Projet 🇸🇳"

log_success "Commit créé avec succès"

# Créer et pousser le tag
log_info "Création du tag $VERSION..."
git tag -a $VERSION -m "SAMA ÉTAT v1.3 Stable

🎯 Version stable avec carte interactive complète et workflow des événements.

Nouvelles fonctionnalités majeures:
- Carte interactive plein écran avec géolocalisation GPS précise
- Workflow événements: Brouillon → Validé → En cours → Terminé
- Création automatique d'événements Odoo lors de la validation
- Double accès: Profil public + Gestion administrative
- Interface responsive compatible tous appareils

Technologies utilisées:
- Leaflet 1.7.1 + MarkerCluster 1.4.1
- OpenStreetMap pour les tuiles cartographiques
- Bootstrap 5 + Font Awesome 6
- Odoo 18 + PostgreSQL 12+

Documentation complète disponible:
- INSTALLATION_GUIDE_v1.3.md
- CHANGELOG_v1.3.md
- DEPENDENCIES_v1.3.md
- README_v1.3.md

Une République Transparente, Projet par Projet 🇸🇳"

log_success "Tag $VERSION créé"

# Afficher les informations avant le push
echo ""
log_info "Résumé de la release:"
echo "  - Version: $VERSION"
echo "  - Branche: $CURRENT_BRANCH"
echo "  - Repository: $REPO_URL"
echo "  - Fichiers modifiés: $(echo "$CHANGES" | wc -l) fichiers"
echo ""

# Demander confirmation pour le push
read -p "🤔 Voulez-vous pousser vers GitHub maintenant? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Push vers GitHub en cours..."
    
    # Push de la branche
    git push origin $CURRENT_BRANCH
    log_success "Branche $CURRENT_BRANCH poussée"
    
    # Push du tag
    git push origin $VERSION
    log_success "Tag $VERSION poussé"
    
    echo ""
    log_success "🎉 Release v1.3 Stable publiée avec succès!"
    echo ""
    echo "📋 Prochaines étapes sur GitHub:"
    echo "  1. Aller sur: $REPO_URL/releases"
    echo "  2. Cliquer sur 'Create a new release'"
    echo "  3. Sélectionner le tag: $VERSION"
    echo "  4. Titre: 'SAMA ÉTAT v1.3 Stable - Carte Interactive & Workflow Événements'"
    echo "  5. Description: Copier le contenu de CHANGELOG_v1.3.md"
    echo "  6. Marquer comme 'Latest release'"
    echo "  7. Publier la release"
    echo ""
    echo "🔗 Liens utiles:"
    echo "  - Repository: $REPO_URL"
    echo "  - Releases: $REPO_URL/releases"
    echo "  - Issues: $REPO_URL/issues"
    echo ""
    echo "📊 Statistiques:"
    echo "  - Commits: $(git rev-list --count HEAD)"
    echo "  - Fichiers: $(find . -name "*.py" -o -name "*.xml" -o -name "*.md" | wc -l) fichiers"
    echo "  - Taille: $(du -sh . | cut -f1)"
    
else
    log_warning "Push annulé. Vous pouvez le faire manuellement avec:"
    echo "  git push origin $CURRENT_BRANCH"
    echo "  git push origin $VERSION"
fi

echo ""
log_success "✨ Script de release terminé!"
echo "🇸🇳 SAMA ÉTAT v1.3 Stable - Une République Transparente, Projet par Projet"
