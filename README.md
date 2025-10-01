# 🏗️ SAMA PROMIS - Program Management Information System

[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-blue.svg)](https://github.com/odoo/odoo)
[![License](https://img.shields.io/badge/License-LGPL--3-green.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Author](https://img.shields.io/badge/Author-SAMA%20Solutions-orange.svg)](https://www.samaetat.sn)
[![Community Edition](https://img.shields.io/badge/Edition-Community-brightgreen.svg)](https://www.odoo.com/page/editions)

## ⚠️ Compatibilité Odoo 18 Community Edition

**Ce module est 100% compatible avec Odoo 18 Community Edition.**

### Prérequis Techniques
- **Python**: 3.11 ou supérieur
- **PostgreSQL**: 13 ou supérieur
- **Odoo**: 18.0 Community Edition

### Modules Odoo Requis (CE uniquement)
- ✅ `base` - Module de base Odoo
- ✅ `mail` - Système de messagerie et notifications
- ✅ `website` - Portail public
- ✅ `project` - Gestion de projets

### ⚠️ Modules NON Requis
Ce module **NE DÉPEND PAS** des modules suivants (Enterprise/absents de CE):
- ❌ `account` - Module comptabilité (Enterprise)

### Fonctionnalités Désactivées (nécessitent Enterprise)
Les fonctionnalités suivantes sont désactivées car elles nécessitent le module `account` (Enterprise):
- Génération automatique d'écritures comptables
- Intégration avec les journaux comptables
- Paiements comptables automatiques

**Alternative CE**: Le module utilise un système de suivi financier simplifié avec des champs monétaires directs, sans intégration comptable.

📖 **Documentation complète**: Voir [ODOO18_CE_COMPATIBILITY.md](./ODOO18_CE_COMPATIBILITY.md)

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
- **Odoo**: 18.0 Community Edition
- **Python**: 3.11 ou supérieur
- **PostgreSQL**: 13 ou supérieur
- **Dépendances Python**: `qrcode`

### Vérification de Compatibilité

Avant l'installation, vérifiez que vous utilisez:
```bash
# Vérifier la version Python
python3 --version  # Doit être >= 3.11

# Vérifier la version PostgreSQL
psql --version  # Doit être >= 13

# Vérifier la version Odoo
odoo --version  # Doit être 18.0 Community Edition
```

### Installation du module

1. **Cloner le repository :**
```bash
git clone https://github.com/sama-solutions/sama_promis.git
cd sama_promis
```

2. **Installer les dépendances Python :**
```bash
pip install qrcode
```

3. **Copier dans addons :**
```bash
cp -r sama_promis /path/to/odoo/addons/
```

4. **Redémarrer Odoo :**
```bash
sudo systemctl restart odoo
# ou
odoo-bin -u sama_promis -d your_database
```

5. **Installer le module :**
- Aller dans Apps
- Rechercher "SAMA PROMIS"
- Cliquer sur "Install"

### Vérification Post-Installation

Après installation, vérifiez que:
- ✅ Aucune erreur liée au module `account`
- ✅ Toutes les vues s'affichent correctement
- ✅ Les listes sont éditables en masse (`multi_edit`)
- ✅ Les QR codes se génèrent correctement

## Validation de l'Installation

### Script de Validation Automatique

Après l'installation, exécutez le script de validation pour vérifier que tous les composants sont correctement chargés:

```bash
# Rendre le script exécutable
chmod +x scripts/validate_module_loading.py

# Exécuter le script
python3 scripts/validate_module_loading.py
```

**Résultat attendu:**
```
============================================================
SAMA PROMIS - Module Loading Validation
============================================================

[1] Checking Mixin Files...
✓ Workflow Mixin exists: /path/to/shared/mixins/workflow_mixin.py
✓ Audit Mixin exists: /path/to/shared/mixins/audit_mixin.py

[2] Checking Import Order...
✓ Import order correct in __init__.py: shared before models

[3] Checking Model Names...
✓ Model name correct in models/call_for_proposal.py: sama.promis.call.proposal
✓ Model name correct in shared/mixins/workflow_mixin.py: sama.promis.workflow.mixin
✓ Model name correct in shared/mixins/audit_mixin.py: sama.promis.audit.mixin

[4] Checking Mixin Inheritance...
✓ Mixin inheritance found in models/compliance_task.py: sama.promis.workflow.mixin
✓ Mixin inheritance found in micromodules/core/models/base_model.py: sama.promis.workflow.mixin
✓ Mixin inheritance found in micromodules/core/models/base_model.py: sama.promis.audit.mixin

[5] Checking call_for_proposal References...
✓ Correct model name in micromodules/projects/models/project.py

[6] Checking One2many Relations...
✓ Correct One2many relation in call_for_proposal.py

============================================================
✓ ALL CHECKS PASSED! Module should load correctly.
============================================================
```

### Vérification Manuelle

Si vous préférez vérifier manuellement:

1. **Vérifier l'ordre d'import dans `__init__.py`:**
   ```python
   from . import shared        # DOIT être en premier
   from . import models
   from . import controllers
   from . import micromodules
   ```

2. **Vérifier le nom du modèle dans `micromodules/projects/models/project.py` ligne 200:**
   ```python
   call_for_proposal_id = fields.Many2one(
       'sama.promis.call.proposal',  # Correct (sans "for")
       ...
   )
   ```

3. **Vérifier la relation One2many dans `models/call_for_proposal.py` ligne 46:**
   ```python
   project_ids = fields.One2many('project.project', 'call_for_proposal_id',
                               string="Projets Soumis")
   ```

### Dépannage

**Erreur: "Model not found: sama.promis.workflow.mixin"**
- Vérifiez que `from . import shared` est présent dans `__init__.py`
- Vérifiez que `from . import mixins` est présent dans `shared/__init__.py`
- Vérifiez que les fichiers mixin existent dans `shared/mixins/`

**Erreur: "Field 'call_for_proposal_id' does not exist"**
- Vérifiez que le nom du modèle est `sama.promis.call.proposal` (sans "for")
- Vérifiez que la relation One2many pointe vers `project.project`

**Erreur: "Invalid field on model"**
- Exécutez le script de validation pour identifier le problème exact
- Vérifiez les logs Odoo pour plus de détails

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

### Version actuelle : 18.0.3.1.0 (Version Hybride) 🎆

**Cette version combine le meilleur de deux versions précédentes :**
- Base moderne avec architecture micromodules
- Améliorations techniques de la version de développement
- Documentation et outils de migration complets

#### 🎯 **Fonctionnalités principales :**
- ✅ Architecture micromodules complète
- ✅ Dashboard public PROMISPUBLIC
- ✅ Page citoyenne "SAMA PROMIS ET MOI"
- ✅ QR codes automatiques
- ✅ Cycles de vie des projets
- ✅ Appels à propositions
- ✅ Gestion des contrats (améliorée)
- ✅ Modèles de contrats avancés avec aperçu
- ✅ Système de paiements
- ✅ Évaluations et indicateurs
- ✅ Scripts de migration robustes
- ✅ Documentation technique complète

#### 🔄 **Historique des versions :**
- `18.0.3.1.0` - Version hybride (actuelle)
- `18.0.3.0.0` - Version avec architecture micromodules
- `18.0.2.0.2` - Version de développement avec améliorations

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