# 🏗️ SAMA PROMIS - Program Management Information System

[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-blue.svg)](https://github.com/odoo/odoo)
[![License](https://img.shields.io/badge/License-LGPL--3-green.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Author](https://img.shields.io/badge/Author-SAMA%20Solutions-orange.svg)](https://www.samaetat.sn)

## 📋 Description

**SAMA PROMIS** est un système de gestion de l'information des programmes (PMIS) conçu pour la gestion des projets de bailleurs de fonds internationaux. Il utilise une architecture micromodules pour une flexibilité et une résilience maximales.

## ✨ Fonctionnalités Principales

### 🏗️ **Architecture Micromodules**
- **Core** - Modèles de base, QR codes, workflows, audit
- **Projects** - Gestion des projets avec cycles de vie complets
- **Public Portal** - Dashboard "PROMISPUBLIC" et page citoyenne
- **Calls** - Appels à propositions
- **Contracts** - Contrats et signatures électroniques
- **Payments** - Gestion des paiements
- **Evaluations** - Évaluations et indicateurs

### 🎯 **Gestion de Projets**
- Cycles de vie complets avec boutons d'action
- Workflows automatisés
- Suivi des étapes et jalons
- Gestion des ressources et budgets
- Rapports de progression

### 📊 **Dashboard Public**
- Interface "PROMISPUBLIC" moderne
- Cartes interactives et filtres
- Visualisation des données en temps réel
- Transparence des projets publics

### 👥 **Page Citoyenne**
- Interface "SAMA PROMIS ET MOI"
- Accès citoyen aux informations
- Participation et feedback
- Suivi des projets locaux

### 🔍 **QR Codes Automatiques**
- Génération automatique pour tous les modèles
- Traçabilité complète
- Accès rapide aux informations
- Intégration mobile

### 📋 **Appels à Propositions**
- Gestion complète des appels
- Soumission en ligne
- Évaluation et sélection
- Suivi des candidatures

### 📄 **Contrats et Signatures**
- Gestion des contrats
- Signatures électroniques
- Suivi des obligations
- Archivage numérique

### 💰 **Gestion des Paiements**
- Planification des paiements
- Suivi des décaissements
- Rapports financiers
- Intégration comptable

### 📈 **Évaluations et Indicateurs**
- Système d'évaluation
- Indicateurs de performance
- Rapports d'impact
- Tableaux de bord analytiques

## 🚀 Installation

### Prérequis
- Odoo 18.0
- Python 3.8+
- PostgreSQL

### Installation du module

1. **Cloner le repository :**
```bash
git clone https://github.com/sama-solutions/sama_promis.git
cd sama_promis
```

2. **Copier dans addons :**
```bash
cp -r sama_promis /path/to/odoo/addons/
```

3. **Redémarrer Odoo :**
```bash
sudo systemctl restart odoo
```

4. **Installer le module :**
- Aller dans Apps
- Rechercher "SAMA PROMIS"
- Cliquer sur "Install"

## 📖 Configuration

### Configuration initiale
1. Configurer les paramètres du système
2. Créer les types de projets
3. Définir les workflows
4. Paramétrer les rôles et permissions

### Configuration des micromodules
1. Activer les micromodules nécessaires
2. Configurer les intégrations
3. Personnaliser les dashboards
4. Définir les indicateurs

## 🛠️ Développement

### Structure du module
```
sama_promis/
├── __manifest__.py          # Manifeste du module
├── __init__.py             # Initialisation
├── models/                 # Modèles de données
├── views/                  # Vues et interfaces
├── controllers/            # Contrôleurs web
├── data/                   # Données initiales
├── security/               # Sécurité et permissions
├── static/                 # Fichiers statiques
├── templates/              # Templates web
├── micromodules/           # Architecture micromodules
├── shared/                 # Composants partagés
├── wizard/                 # Assistants
└── tests/                  # Tests unitaires
```

### Micromodules principaux
- `core/` - Fonctionnalités de base
- `projects/` - Gestion de projets
- `public_portal/` - Portail public
- `calls/` - Appels à propositions
- `contracts/` - Gestion des contrats
- `payments/` - Système de paiement
- `evaluations/` - Évaluations

## 🧪 Tests

### Lancer les tests
```bash
python -m pytest tests/
```

### Tests disponibles
- Tests unitaires des modèles
- Tests d'intégration des micromodules
- Tests de l'interface web
- Tests de performance

## 📈 Versions

### Version actuelle : 18.0.3.0.0
- ✅ Architecture micromodules complète
- ✅ Dashboard public PROMISPUBLIC
- ✅ Page citoyenne "SAMA PROMIS ET MOI"
- ✅ QR codes automatiques
- ✅ Cycles de vie des projets
- ✅ Appels à propositions
- ✅ Gestion des contrats
- ✅ Système de paiements
- ✅ Évaluations et indicateurs

## 🤝 Contribution

### Comment contribuer
1. Fork le projet
2. Créer une branche feature
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

### Standards de code
- Suivre les conventions Odoo
- Documenter le code
- Ajouter des tests
- Respecter l'architecture micromodules

## 📞 Support

### Contact
- **Auteur :** SAMA Transparent State Solutions
- **Website :** https://www.samaetat.sn
- **Email :** contact@samaetat.sn

### Issues
Pour signaler un bug ou demander une fonctionnalité :
[Créer une issue](https://github.com/sama-solutions/sama_promis/issues)

## 📄 Licence

Ce projet est sous licence LGPL-3. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

Merci à tous les contributeurs et à la communauté Odoo pour leur soutien.

---

**Développé avec ❤️ par SAMA Transparent State Solutions**