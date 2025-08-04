# 🗺️ Carte Interactive SAMA ÉTAT - Coordonnées Réalistes

## Vue d'ensemble

Ce document décrit la mise en place d'une carte interactive pour le tableau de bord public de SAMA ÉTAT, avec des coordonnées GPS réalistes pour toutes les villes et régions du Sénégal.

## 🎯 Objectifs

- **Pour les citoyens** : Visualiser facilement les projets, décisions et événements gouvernementaux dans leur région
- **Transparence** : Afficher automatiquement tous les éléments avec coordonnées GPS
- **Accessibilité** : Tooltips informatifs en français avec informations pertinentes
- **Couverture nationale** : Représentation équilibrée de toutes les régions du Sénégal

## 📍 Coordonnées Implémentées

### Villes Principales

| Ville | Latitude | Longitude | Description |
|-------|----------|-----------|-------------|
| **Dakar** | 14.716677 | -17.467686 | Capitale politique et économique |
| **Saint-Louis** | 16.026340 | -16.489649 | Ancienne capitale, site UNESCO |
| **Thiès** | 14.788889 | -16.936111 | Carrefour ferroviaire |
| **Kaolack** | 14.151515 | -16.077778 | Port fluvial, centre commercial |
| **Ziguinchor** | 12.548267 | -16.263982 | Capitale de la Casamance |
| **Tambacounda** | 13.771944 | -13.671006 | Porte de l'est du Sénégal |
| **Kédougou** | 12.557892 | -12.179688 | Centre minier |
| **Louga** | 15.619166 | -16.226111 | Région pastorale |
| **Diourbel** | 14.654722 | -16.231944 | Bassin arachidier |
| **Matam** | 15.655647 | -13.255615 | Vallée du fleuve Sénégal |

### Distribution Géographique

- **Nord** (lat > 15°) : 3 localités (Saint-Louis, Louga, Matam)
- **Centre** (13.5° ≤ lat ≤ 15°) : 5 localités (Dakar, Thiès, Kaolack, Diourbel, Tambacounda)
- **Sud** (lat < 13.5°) : 2 localités (Ziguinchor, Kédougou)
- **Ouest** (lng < -16°) : 7 localités (côte atlantique)
- **Est** (lng > -14°) : 3 localités (frontière malienne)

## 🚀 Fonctionnalités

### 1. Carte Interactive
- **Technologie** : Leaflet.js avec tuiles OpenStreetMap
- **Vue par défaut** : Centrée sur le Sénégal (14.5°N, 14.5°W)
- **Zoom intelligent** : Ajustement automatique selon les marqueurs visibles

### 2. Types de Marqueurs

#### 🔵 Projets (P)
- **Couleur** : Bleu (#007bff)
- **Données** : Nom, description, statut, avancement, dates, ministère
- **Tooltip** : Informations citoyennes sur l'impact local

#### 🟡 Décisions (D)
- **Couleur** : Jaune (#ffc107)
- **Données** : Titre, type (décret/arrêté), référence, date, ministère
- **Tooltip** : Implications pour les citoyens

#### 🔵 Événements (E)
- **Couleur** : Bleu clair (#17a2b8)
- **Données** : Nom, type, date, lieu, organisateur
- **Tooltip** : Informations de participation publique

### 3. Filtres Interactifs
- Cases à cocher pour chaque type d'élément
- Compteurs en temps réel
- Mise à jour instantanée de la carte

## 📊 Données Démonstration

### Projets Gouvernementaux (25+)
- Répartis dans toutes les régions
- Statuts variés : En cours, Validé, Achevé, En préparation
- Secteurs : Agriculture, Santé, Éducation, Infrastructure, Numérique

### Décisions Officielles (15+)
- Types : Décrets, Arrêtés, Circulaires
- Répartition géographique équilibrée
- Statuts de mise en œuvre

### Événements Publics (20+)
- Conférences, Ateliers, Forums, Cérémonies
- Calendrier étalé sur 2025-2026
- Couverture nationale

## 🛠️ Installation

### 1. Fichiers Modifiés/Ajoutés
```
sama_etat/
├── data/
│   ├── senegalese_locations_demo.xml          # NOUVEAU
│   ├── government_projects_demo_data.xml      # MIS À JOUR
│   ├── government_decisions_demo.xml          # MIS À JOUR
│   ├── government_events_demo_data.xml        # MIS À JOUR
│   └── demo_data.xml                          # MIS À JOUR
├── views/
│   └── public_map.xml                         # AMÉLIORÉ
├── controllers/
│   └── public_controllers.py                  # AMÉLIORÉ
└── __manifest__.py                            # MIS À JOUR
```

### 2. Installation des Données
```bash
# 1. Redémarrer Odoo avec mise à jour du module
./odoo-bin -d votre_db -u sama_etat

# 2. Vérifier les données
python3 test_coordinates.py
```

### 3. Accès Public
- **URL** : `http://votre-serveur/senegal2050/dashboard`
- **Section** : "Carte Interactive des Projets, Décisions et Événements Publics"

## 🔧 Configuration Technique

### API Endpoint
```javascript
POST /sama_etat/get_map_data
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "call", 
  "params": {}
}
```

### Réponse API
```json
{
  "result": {
    "projects": [
      {
        "id": 1,
        "name": "Nom du projet",
        "description": "Description...",
        "latitude": 14.716677,
        "longitude": -17.467686,
        "status": "in_progress",
        "progress": 65.5,
        "ministry_id": [1, "Ministère"]
      }
    ],
    "decisions": [...],
    "events": [...]
  }
}
```

### Modèles avec Coordonnées
- `government.project` : latitude, longitude
- `government.decision` : latitude, longitude  
- `government.event` : latitude, longitude
- `project.public.location.commune` : latitude, longitude

## 🎨 Interface Utilisateur

### Tooltips Citoyens
- **Projets** : Impact sur la région, statut d'avancement, dates clés
- **Décisions** : Type officiel, implications pratiques, références
- **Événements** : Participation publique, dates, lieux précis

### Responsive Design
- **Desktop** : Carte 500px de hauteur
- **Mobile** : Ajustement automatique
- **Interactions** : Touch-friendly sur mobile

## 🧪 Tests et Validation

### Script de Test
```bash
python3 test_coordinates.py
```

### Vérifications
- ✅ Coordonnées dans les limites du Sénégal
- ✅ Distribution géographique équilibrée
- ✅ API endpoint fonctionnel
- ✅ Tooltips informatifs

### Limites Géographiques du Sénégal
- **Latitude** : 12.0° à 16.8° Nord
- **Longitude** : -17.5° à -11.3° Ouest

## 🔮 Évolutions Futures

### Fonctionnalités Prévues
1. **Recherche géographique** : Filtrer par région/département
2. **Clustering** : Regroupement des marqueurs proches
3. **Couches thématiques** : Affichage par secteur d'activité
4. **Mode satellite** : Vue satellite en option
5. **Export de données** : Téléchargement des informations

### Données Supplémentaires
1. **Projets en temps réel** : Intégration avec le système de suivi
2. **Indicateurs KPI** : Affichage des performances par région
3. **Calendrier événements** : Synchronisation avec agenda public
4. **Statistiques régionales** : Données démographiques et économiques

## 📞 Support

### Contact Technique
- **Documentation** : Consulter les commentaires dans le code
- **Tests** : Utiliser `test_coordinates.py`
- **Logs** : Vérifier la console navigateur pour les erreurs JavaScript

### Dépannage Courant
1. **Carte ne s'affiche pas** : Vérifier la connexion Internet (OpenStreetMap)
2. **Pas de marqueurs** : Vérifier que les données ont des coordonnées GPS
3. **Tooltips vides** : Contrôler le format des données de l'API
4. **Performance lente** : Limiter le nombre de marqueurs affichés

## 📄 Licence
Ce module fait partie de SAMA ÉTAT - Système de gestion publique du Sénégal.
Développé pour la transparence gouvernementale et l'engagement citoyen.

---
*Dernière mise à jour : Juillet 2024*
*Version : 1.0.0*