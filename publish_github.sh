#!/bin/bash

# Script de publication directe GitHub pour SAMA ÉTAT v1.3 Stable
# Ce script évite les problèmes de sélecteur de shell

echo "🚀 Publication SAMA ÉTAT v1.3 Stable sur GitHub..."

# Aller dans le répertoire
cd /home/grand-as/psagsn/custom_addons/sama_etat

# Vérifier si c'est un repo Git
if [ ! -d ".git" ]; then
    echo "📁 Initialisation du repository Git..."
    git init
    git remote add origin https://github.com/loi200812/sama-etat.git
fi

# Vérifier la configuration Git
if [ -z "$(git config user.name)" ]; then
    echo "⚙️ Configuration Git..."
    git config user.name "SAMA ÉTAT Team"
    git config user.email "contact@sama-etat.sn"
fi

# Ajouter tous les fichiers
echo "📝 Ajout des fichiers..."
git add .

# Créer le commit
echo "💾 Création du commit v1.3 stable..."
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

# Créer le tag
echo "🏷️ Création du tag v1.3-stable..."
git tag -a v1.3-stable -m "SAMA ÉTAT v1.3 Stable - Carte Interactive & Workflow Événements

🎯 Version stable avec toutes les nouvelles fonctionnalités
- Carte interactive complète avec géolocalisation GPS
- Workflow événements avec création automatique Odoo
- Documentation complète et professionnelle
- Interface responsive moderne

Une République Transparente, Projet par Projet 🇸🇳"

# Pousser vers GitHub
echo "📤 Publication sur GitHub..."
git push origin main
git push origin v1.3-stable

echo "✅ Publication terminée !"
echo "🔗 Vérifiez sur : https://github.com/loi200812/sama-etat"
echo "🏷️ Tag créé : v1.3-stable"
echo "📋 Prochaine étape : Créer la release sur GitHub avec RELEASE_NOTES_v1.3.md"
