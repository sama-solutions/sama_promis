# Données de Démonstration - Module Sénégal Gov Project Management

## Vue d'ensemble

Ce module contient des données de démonstration réalistes pour le système de gestion de projets gouvernementaux du Sénégal, alignées sur le Plan Sénégal 2050.

## Fichiers de données créés

### 1. strategic_objectives_demo_data.xml
Structure complète du Plan Sénégal 2050 :
- **1 Plan stratégique national** : Plan Sénégal 2050
- **4 Piliers stratégiques** :
  - Capital Humain et Social (CHS)
  - Transformation Économique (TE)  
  - Gouvernance et Paix (GP)
  - Développement Territorial (DT)
- **6 Axes stratégiques** : Éducation, Santé, Emploi des Jeunes, Agriculture, Industrie, Économie Numérique
- **15 Objectifs stratégiques** avec codes et descriptions détaillées
- **5 KPIs** avec valeurs cibles et actuelles

### 2. ministries_demo_data.xml
Structure gouvernementale complète du Sénégal (2024) :
- **27 Ministères et institutions** incluant :
  - Présidence de la République
  - Ministères régaliens (Intérieur, Défense, Justice, Affaires Étrangères)
  - Ministères économiques (Finances, Économie, Commerce, Industrie)
  - Ministères sociaux (Santé, Éducation, Emploi, Jeunesse)
  - Ministères techniques (Agriculture, Infrastructures, Énergie, Numérique)
  - Secrétariats d'État spécialisés

Chaque ministère contient :
- Nom officiel complet
- Code ministériel 
- Type d'institution
- Description des missions
- Coordonnées complètes (adresse, téléphone, email)

### 3. government_projects_demo_data.xml
**16 Projets gouvernementaux réalistes** couvrant tous les secteurs :

#### Secteur Éducation
- Réforme du Système Éducatif Sénégalais (2025-2027)
- Écoles Numériques du Sénégal (2025-2026)

#### Secteur Santé
- Couverture Sanitaire Universelle 2025 (en cours)
- Modernisation des Infrastructures Sanitaires (2025-2028)

#### Secteur Agriculture
- Programme d'Autosuffisance en Riz (2025-2030)
- Mécanisation de l'Agriculture Sénégalaise (2025-2027)

#### Secteur Emploi
- Fonds d'Appui à l'Entrepreneuriat des Jeunes (2025-2027)
- Programme National de Formation des Jeunes (2025-2027)

#### Secteur Industrie
- Zones Économiques Spéciales du Sénégal (2025-2028)
- Promotion du Contenu Local dans l'Industrie (2025-2027)

#### Secteur Numérique
- Déploiement de la Fibre Optique Nationale (2025-2026)
- Plateforme Nationale d'e-Gouvernement (2025-2026)

#### Infrastructure & Énergie
- Programme National de Désenclavement (2025-2027)
- Mix Énergétique 2030 - Énergies Renouvelables (2025-2029)
- Accès Universel à l'Eau Potable (2025-2028)

#### Projets Transversaux
- Villes Intelligentes du Sénégal (2025-2027)

### 4. budgets_demo_data.xml
**11 Budgets sectoriels réalistes** pour l'année 2025 :
- Budgets en francs CFA (FCFA)
- Montants alloués vs utilisés pour tracking
- Lien avec les ministères et objectifs stratégiques

**Principaux budgets :**
- Éducation : 850 milliards FCFA
- Infrastructures : 920 milliards FCFA  
- Santé : 680 milliards FCFA
- Énergie : 560 milliards FCFA
- Agriculture : 420 milliards FCFA
- Industrie : 390 milliards FCFA
- Numérique : 310 milliards FCFA
- Emploi des Jeunes : 280 milliards FCFA
- Hydraulique : 240 milliards FCFA
- Fonds d'Urgence Nationale : 150 milliards FCFA
- Budget Diaspora : 75 milliards FCFA

## Fonctionnalités activées

✅ **Connexion intégrée** : Projets gouvernementaux ↔ Projets Odoo
✅ **Assistant de création** : Wizard pour créer des projets gouvernementaux depuis Odoo
✅ **Synchronisation bidirectionnelle** : Données partagées entre les deux systèmes
✅ **Suivi budgétaire** : Liaison projets-budgets-ministères
✅ **Tableau de bord stratégique** : Vision Plan Sénégal 2050 complète

## Accès au système

- **URL** : http://localhost:8070
- **Base de données** : govtech
- **Interface** : Menu "Plan Sénégal 2050" dans Odoo

## Statut des projets

Les projets ont différents statuts pour démonstration :
- **En cours** : 4 projets (Santé universelle, Fibre optique, etc.)
- **Validés** : 8 projets (Réforme éducation, Agriculture, etc.)  
- **Brouillons** : 4 projets (Infrastructures sanitaires, Smart cities, etc.)

Cette structure permet de tester toutes les fonctionnalités du workflow gouvernemental sénégalais.
