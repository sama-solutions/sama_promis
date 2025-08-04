# SAMA ÉTAT v1.3 Stable - Plan Sénégal 2050 🇸🇳

[![Version](https://img.shields.io/badge/version-1.3%20stable-brightgreen)](https://github.com/loi200812/sama-etat)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Odoo](https://img.shields.io/badge/Odoo-18.0-purple.svg)](https://www.odoo.com)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)

## 🎯 Nouveautés Version 1.3

### 🗺️ **Carte Interactive Complète**
- **Visualisation plein écran** avec géolocalisation GPS précise
- **Filtrage dynamique** par projets, décisions, événements
- **Clustering intelligent** des marqueurs pour une meilleure lisibilité
- **Interface responsive** compatible mobile, tablette et desktop
- **Navigation fluide** avec bouton "Ajuster la vue"

### 📅 **Workflow Événements Gouvernementaux**
- **Cycle de vie complet** : Brouillon → Validé → En cours → Terminé
- **Création automatique** d'événements Odoo lors de la validation
- **Double accès** : Profil public + Gestion administrative
- **Intégration calendrier** avec synchronisation Odoo

## 📖 Description

SAMA ÉTAT est une plateforme numérique open source conçue pour digitaliser intégralement la gouvernance publique vers le zéro-papier. Elle vise à structurer, piloter et rendre visible toute action publique, au service d'une République transparente, performante et inclusive.

### 🎯 Une plateforme pensée pour résoudver un vrai problème public

Aujourd'hui, les projets gouvernementaux sont trop souvent dispersés, peu traçables, et inaccessibles aux citoyens. SAMA ÉTAT centralise l'information, connecte les décisions, aligne les parties prenantes et outille les citoyens.

Elle transforme l'État, non par promesse, mais par architecture logicielle.

## 🚀 Fonctionnalités Principales

### 🗺️ **Carte Interactive**
```
┌─────────────────────────────────────────┐
│ [← Retour au tableau de bord]           │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │                                 │    │
│  │        CARTE LEAFLET            │    │
│  │     avec marqueurs et           │    │
│  │      clustering                 │    │
│  │                                 │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌─ Filtres ─┐  ┌─ Actions ─┐          │
│  │☑ Projets  │  │ Ajuster   │          │
│  │☑ Décisions│  │ la vue    │          │
│  │☑ Événements│  └───────────┘          │
│  └───────────┘                         │
└─────────────────────────────────────────┘
```

**Caractéristiques :**
- 🏗️ **Projets** : Marqueurs bleus avec géolocalisation précise
- ⚖️ **Décisions** : Marqueurs verts avec contexte géographique
- 📅 **Événements** : Marqueurs oranges avec informations détaillées
- 🎯 **Clustering** : Regroupement automatique pour éviter la surcharge
- 📱 **Responsive** : Interface adaptée à tous les écrans

### 📋 **Gestion des Projets Gouvernementaux**
- Regroupe et structure tous les projets publics sous une feuille de route unique
- Suit en temps réel l'avancement avec indicateurs visuels
- Connecte les projets aux objectifs stratégiques du Plan Sénégal 2050
- Intègre la gestion budgétaire et les sources de financement

### 📅 **Événements Gouvernementaux**
```
Brouillon ──[Valider]──→ Validé ──[Démarrer]──→ En cours ──[Terminer]──→ Terminé
    ↑                                                                      
    └──────────────────[Modifier]──────────────────────────────────────────┘
```

**Actions disponibles :**
- **Modifier** : Remet en brouillon pour modification
- **Valider** : Crée automatiquement l'événement Odoo
- **Profil public** : Accès à la page publique
- **Voir l'exécution** : Ouverture dans le calendrier Odoo

### ⚖️ **Décisions Gouvernementales**
- Suit les décisions du Président, Premier Ministre, Conseil des ministres
- Connecte les décisions aux projets et événements
- Archive et rend accessible l'historique décisionnel
- Géolocalise les impacts territoriaux

### 🌐 **Interface Publique**
- **Tableau de bord citoyen** : Vue d'ensemble accessible à tous
- **Pages dédiées** : Fiches détaillées pour chaque élément
- **Navigation intuitive** : Interface moderne et ergonomique
- **Accès mobile** : Optimisé pour smartphones et tablettes

## 🛠️ Technologies Utilisées

### 🐍 **Backend**
- **Odoo 18** : Framework ERP open source
- **Python 3.8+** : Langage de programmation principal
- **PostgreSQL 12+** : Base de données relationnelle

### 🌐 **Frontend**
- **Leaflet 1.7.1** : Bibliothèque cartographique open source
- **MarkerCluster 1.4.1** : Regroupement intelligent des marqueurs
- **Bootstrap 5** : Framework CSS responsive
- **Font Awesome 6** : Bibliothèque d'icônes
- **JavaScript ES6** : Interactions dynamiques

### 🗺️ **Cartographie**
- **OpenStreetMap** : Tuiles cartographiques libres
- **GeoPy** : Géocodage et calculs géographiques
- **Coordonnées GPS** : Géolocalisation précise des éléments

## 📦 Installation Rapide

### 🔧 **Prérequis**
```bash
# Système
Ubuntu 20.04+ ou Debian 11+
Python 3.8+
PostgreSQL 12+
Git

# Ressources
RAM: 4GB (8GB recommandé)
CPU: 2 cores (4 cores recommandé)
Stockage: 20GB (50GB recommandé)
```

### 🚀 **Installation**
```bash
# 1. Cloner le repository
git clone https://github.com/loi200812/sama-etat.git
cd sama-etat
git checkout v1.3-stable

# 2. Installer Odoo 18
# Suivre le guide : INSTALLATION_GUIDE_v1.3.md

# 3. Copier le module
cp -r sama_etat /path/to/odoo/addons/

# 4. Installer les dépendances
pip3 install -r requirements.txt

# 5. Démarrer Odoo
python3 odoo-bin -c odoo.conf -d sama_db -i sama_etat
```

### 🐳 **Installation Docker**
```bash
# Cloner et démarrer
git clone https://github.com/loi200812/sama-etat.git
cd sama-etat
docker-compose up -d

# Accéder à l'application
# http://localhost:8069
```

## 🌐 Accès à l'Application

### 📱 **URLs Publiques**
```
🏠 Tableau de bord : /senegal2050/dashboard
🗺️ Carte interactive : /senegal2050/fullscreen_map
🏗️ Projet public : /senegal2050/project/{id}
📅 Événement public : /senegal2050/event/{id}
⚖️ Décision publique : /senegal2050/decision/{id}
```

### 🔐 **Interface Administrative**
```
👤 Connexion : http://localhost:8069
📊 Projets : Menu > Projets Gouvernementaux
📅 Événements : Menu > Événements Publics
⚖️ Décisions : Menu > Décisions Gouvernementales
📅 Calendrier : Menu > Calendrier (événements Odoo)
```

## 📊 Avantages par Acteur

### 🏛️ **Pour le Gouvernement**
- ✅ Tableau de bord centralisé du Plan Sénégal 2050
- ✅ Outil unique pour coordonner et contrôler les politiques publiques
- ✅ **Carte interactive** avec géolocalisation de tous les projets
- ✅ Zéro coût de licence, 100% open source
- ✅ Plateforme qui institutionnalise la reddition de comptes

### 👥 **Pour les Citoyens**
- ✅ Accès transparent aux projets gouvernementaux
- ✅ **Visualisation cartographique** des actions publiques
- ✅ Suivi en temps réel de l'avancement des projets
- ✅ Interface publique accessible sans connexion
- ✅ République responsable, projet par projet

### 🏢 **Pour les Entreprises et ONG**
- ✅ Outil d'alignement avec les feuilles de route gouvernementales
- ✅ **Géolocalisation** des opportunités de partenariat
- ✅ Visibilité sur les projets et budgets publics
- ✅ Plateforme de collaboration avec l'administration

## 🎨 Captures d'Écran

### 🗺️ **Carte Interactive Plein Écran**
- Interface moderne avec contrôles flottants
- Filtrage en temps réel par type d'élément
- Clustering automatique des marqueurs
- Popups informatifs avec liens vers les fiches

### 📋 **Workflow des Événements**
- Boutons d'action contextuels selon le statut
- Barres de progression visuelles
- Accès séparé public/gestion
- Création automatique d'événements Odoo

### 📊 **Tableau de Bord Public**
- Statistiques en temps réel
- Cartes de synthèse interactives
- Navigation intuitive vers les détails
- Design responsive et moderne

## 🔄 Migration et Mise à Jour

### 📋 **Depuis v1.2**
```bash
# Sauvegarde
pg_dump -U user db_name > backup_v1.2.sql

# Mise à jour
git pull origin v1.3-stable
cp -r sama_etat /path/to/odoo/addons/

# Mise à jour module
python3 odoo-bin -c odoo.conf -d db_name -u sama_etat --stop-after-init
```

### 🆕 **Nouvelles Fonctionnalités**
- **Carte interactive** : Automatiquement disponible après mise à jour
- **Workflow événements** : Événements existants migrés vers nouveau workflow
- **Corrections bugs** : Erreurs XML et JavaScript résolues

## 🧪 Tests et Validation

### ✅ **Tests Automatisés**
```bash
# Tests fonctionnels
python3 -m pytest tests/

# Tests carte interactive
curl -I http://localhost:8069/senegal2050/fullscreen_map

# Tests API
curl http://localhost:8069/sama_etat/get_map_data
```

### 🔍 **Checklist Validation**
- [ ] Interface Odoo accessible
- [ ] Module SAMA ÉTAT installé
- [ ] Carte interactive fonctionnelle
- [ ] Filtres de carte opérationnels
- [ ] Workflow événements actif
- [ ] Pages publiques accessibles

## 📚 Documentation

### 📖 **Guides Disponibles**
- **[INSTALLATION_GUIDE_v1.3.md](INSTALLATION_GUIDE_v1.3.md)** : Guide d'installation détaillé
- **[CHANGELOG_v1.3.md](CHANGELOG_v1.3.md)** : Nouveautés et corrections
- **[DEPENDENCIES_v1.3.md](DEPENDENCIES_v1.3.md)** : Dépendances complètes
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** : Documentation API

### 🔗 **Liens Utiles**
- **Repository GitHub** : [https://github.com/loi200812/sama-etat](https://github.com/loi200812/sama-etat)
- **Issues** : [https://github.com/loi200812/sama-etat/issues](https://github.com/loi200812/sama-etat/issues)
- **Wiki** : [https://github.com/loi200812/sama-etat/wiki](https://github.com/loi200812/sama-etat/wiki)

## 🤝 Contribution

### 🔧 **Développement**
```bash
# Fork du repository
git clone https://github.com/YOUR_USERNAME/sama-etat.git

# Créer une branche
git checkout -b feature/nouvelle-fonctionnalite

# Développer et tester
# ...

# Soumettre une Pull Request
```

### 🐛 **Signaler un Bug**
1. Vérifier que le bug n'existe pas déjà dans les [Issues](https://github.com/loi200812/sama-etat/issues)
2. Créer une nouvelle issue avec :
   - Description détaillée
   - Étapes de reproduction
   - Environnement (OS, version Odoo, etc.)
   - Captures d'écran si pertinentes

### 💡 **Proposer une Fonctionnalité**
1. Créer une issue avec le label `enhancement`
2. Décrire le besoin et la solution proposée
3. Discuter avec la communauté
4. Implémenter si approuvé

## 🔮 Roadmap

### 🎯 **Version 1.4 (Prévue Q2 2025)**
- **Notifications push** : Alertes en temps réel
- **Export PDF** : Rapports automatisés
- **API REST** : Intégration systèmes tiers
- **Analytics avancés** : Tableaux de bord BI
- **Mobile App** : Application native

### 🎯 **Version 2.0 (Prévue Q4 2025)**
- **IA/ML** : Prédictions et recommandations
- **Blockchain** : Traçabilité et transparence
- **Multi-tenant** : Support multi-pays
- **Workflow avancé** : Automatisation poussée

## 📄 Licence

Ce projet est sous licence **MIT** - voir le fichier [LICENSE](LICENSE) pour plus de détails.

### 🆓 **Utilisation Libre**
- ✅ Utilisation commerciale
- ✅ Modification
- ✅ Distribution
- ✅ Usage privé

### 📋 **Conditions**
- 📄 Inclure la licence et le copyright
- 📄 Mentionner les modifications apportées

## 👥 Équipe et Remerciements

### 🏗️ **Équipe Principale**
- **Développement** : Équipe SAMA ÉTAT
- **Architecture** : Spécialistes Odoo
- **Design** : Experts UX/UI
- **Tests** : Communauté open source

### 🙏 **Remerciements**
- **Communauté Odoo** : Framework et support
- **OpenStreetMap** : Données cartographiques libres
- **Leaflet** : Bibliothèque cartographique open source
- **Contributeurs** : Tous les développeurs ayant participé

## 📞 Support

### 🆘 **Aide et Support**
- **Documentation** : Guides complets disponibles
- **GitHub Issues** : Support communautaire
- **Wiki** : Base de connaissances collaborative

### 📧 **Contact**
- **Issues GitHub** : Pour bugs et fonctionnalités
- **Discussions** : Pour questions générales
- **Email** : contact@sama-etat.sn (si configuré)

---

## 🎉 Démarrer Maintenant !

```bash
# Installation rapide
git clone https://github.com/loi200812/sama-etat.git
cd sama-etat
docker-compose up -d

# Accéder à l'application
# http://localhost:8069/senegal2050/dashboard
```

**SAMA ÉTAT v1.3 Stable** - Une République Transparente, Projet par Projet 🇸🇳

[![Démarrer](https://img.shields.io/badge/Démarrer-maintenant-success?style=for-the-badge)](https://github.com/loi200812/sama-etat)
[![Documentation](https://img.shields.io/badge/Lire-la%20documentation-blue?style=for-the-badge)](INSTALLATION_GUIDE_v1.3.md)
[![Contribuer](https://img.shields.io/badge/Contribuer-au%20projet-orange?style=for-the-badge)](https://github.com/loi200812/sama-etat/issues)
