# 📦 Dépendances SAMA ÉTAT v1.3 Stable

## 🎯 Vue d'ensemble

Ce document liste toutes les dépendances requises pour SAMA ÉTAT v1.3, incluant les nouvelles fonctionnalités de **carte interactive** et **workflow des événements**.

## 🐍 Dépendances Python

### 📋 **Requises (requirements.txt)**
```txt
# Odoo 18 Core Dependencies
odoo==18.0

# Image Processing (pour QR codes et cartes)
Pillow>=8.3.2
qrcode[pil]>=7.3.1

# Géolocalisation (pour coordonnées GPS)
geopy>=2.2.0

# Utilitaires
python-dateutil>=2.8.2
requests>=2.25.1
```

### 🔧 **Installation**
```bash
# Installation via pip
pip3 install -r requirements.txt

# Ou installation individuelle
pip3 install Pillow qrcode[pil] geopy python-dateutil requests
```

## 🗄️ Dépendances Base de Données

### 🐘 **PostgreSQL**
```bash
# Version minimale
PostgreSQL >= 12.0

# Extensions recommandées
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "unaccent";

# Configuration optimale
shared_preload_libraries = 'pg_stat_statements'
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
```

## 🌐 Dépendances Frontend

### 🗺️ **Bibliothèques Cartographiques**
```html
<!-- Leaflet (Carte interactive) -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>

<!-- MarkerCluster (Regroupement marqueurs) -->
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css" />
<script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>
```

### 🎨 **Frameworks CSS**
```html
<!-- Bootstrap 5 (Interface responsive) -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>

<!-- Font Awesome (Icônes) -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
```

## 🔧 Dépendances Système

### 🖥️ **Système d'Exploitation**
```bash
# Distributions supportées
Ubuntu 20.04+ LTS
Debian 11+
CentOS 8+
RHEL 8+

# Packages système requis
sudo apt install -y python3-dev python3-pip python3-venv
sudo apt install -y build-essential libssl-dev libffi-dev
sudo apt install -y libjpeg-dev libpng-dev libfreetype6-dev
sudo apt install -y libxml2-dev libxslt1-dev zlib1g-dev
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y git curl wget
```

### 🐳 **Docker (Optionnel)**
```yaml
# Version Docker Compose
version: '3.8'

# Images utilisées
postgres:13
odoo:18
nginx:alpine (pour production)
```

## 📊 Modules Odoo Requis

### 🔧 **Modules Core**
```python
# Dans __manifest__.py
'depends': [
    'base',
    'web',
    'website',
    'calendar',          # Nouveau : pour événements Odoo
    'project',           # Gestion projets
    'mail',              # Messagerie
    'portal',            # Accès public
    'website_sale',      # Fonctionnalités web
]
```

### 📦 **Modules Optionnels**
```python
# Modules recommandés pour fonctionnalités avancées
'optional_depends': [
    'hr',                # Ressources humaines
    'account',           # Comptabilité
    'purchase',          # Achats
    'stock',             # Inventaire
    'crm',               # CRM
]
```

## 🌍 APIs Externes

### 🗺️ **Services Cartographiques**
```javascript
// OpenStreetMap (Gratuit)
const osmUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

// Alternatives payantes (optionnel)
// MapBox, Google Maps, IGN (France)
```

### 📍 **Géocodage**
```python
# GeoPy - Conversion adresses en coordonnées
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="sama_etat")

# APIs alternatives
# Google Geocoding API
# MapBox Geocoding API
```

## 📱 Compatibilité Navigateurs

### ✅ **Navigateurs Supportés**
```
Chrome >= 90
Firefox >= 88
Safari >= 14
Edge >= 90
Opera >= 76

# Fonctionnalités requises
ES6 Support
CSS Grid
Flexbox
WebGL (pour cartes)
```

### 📱 **Appareils Mobiles**
```
iOS Safari >= 14
Chrome Mobile >= 90
Samsung Internet >= 14
```

## 🔒 Dépendances Sécurité

### 🛡️ **Certificats SSL**
```bash
# Let's Encrypt (Gratuit)
sudo apt install certbot python3-certbot-nginx

# Ou certificats commerciaux
# Comodo, DigiCert, GlobalSign
```

### 🔐 **Authentification**
```python
# Odoo Authentication (inclus)
# OAuth2 (optionnel)
# LDAP/Active Directory (optionnel)
```

## ⚡ Optimisations Performance

### 🚀 **Cache Redis (Optionnel)**
```bash
# Installation Redis
sudo apt install redis-server

# Configuration Odoo
# Dans odoo.conf
[options]
enable_redis = True
redis_host = localhost
redis_port = 6379
```

### 📊 **Monitoring**
```bash
# Outils recommandés
htop                 # Monitoring système
postgresql-contrib   # Statistiques PostgreSQL
nginx               # Reverse proxy
fail2ban            # Protection brute force
```

## 🧪 Dépendances Développement

### 🔧 **Outils de Développement**
```bash
# Python
pip3 install black flake8 pytest

# JavaScript
npm install -g eslint prettier

# Git hooks
pip3 install pre-commit
```

### 📝 **Documentation**
```bash
# Génération documentation
pip3 install sphinx sphinx-rtd-theme

# Diagrammes
pip3 install plantuml
```

## 📋 Checklist Installation

### ✅ **Vérifications Pré-Installation**
- [ ] Python 3.8+ installé
- [ ] PostgreSQL 12+ configuré
- [ ] Git disponible
- [ ] Connexion internet stable
- [ ] Droits administrateur

### ✅ **Vérifications Post-Installation**
- [ ] Odoo démarre sans erreur
- [ ] Module SAMA ÉTAT installé
- [ ] Carte interactive fonctionnelle
- [ ] Pages publiques accessibles
- [ ] Workflow événements opérationnel

## 🔄 Versions Compatibles

### 📊 **Matrice de Compatibilité**
```
SAMA ÉTAT v1.3 Stable
├── Odoo 18.0 ✅
├── Python 3.8+ ✅
├── PostgreSQL 12+ ✅
├── Ubuntu 20.04+ ✅
├── Debian 11+ ✅
└── CentOS 8+ ✅
```

### 🚫 **Versions Non Supportées**
```
❌ Odoo < 18.0
❌ Python < 3.8
❌ PostgreSQL < 12
❌ Ubuntu < 20.04
❌ Internet Explorer
```

## 🆘 Résolution Problèmes Dépendances

### ❌ **Erreurs Courantes**

#### **Pillow Installation Error**
```bash
# Solution Ubuntu/Debian
sudo apt install libjpeg-dev zlib1g-dev
pip3 install --upgrade pip
pip3 install Pillow

# Solution CentOS/RHEL
sudo yum install libjpeg-devel zlib-devel
pip3 install Pillow
```

#### **PostgreSQL Connection Error**
```bash
# Vérifier service
sudo systemctl status postgresql

# Reconfigurer
sudo -u postgres psql
ALTER USER postgres PASSWORD 'newpassword';
```

#### **Leaflet Map Not Loading**
```javascript
// Vérifier CDN
console.log(typeof L); // Should return 'object'

// Alternative CDN
// https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.js
```

## 📞 Support Dépendances

### 🔗 **Liens Utiles**
- **Odoo Documentation** : [https://www.odoo.com/documentation/18.0/](https://www.odoo.com/documentation/18.0/)
- **Leaflet Documentation** : [https://leafletjs.com/reference.html](https://leafletjs.com/reference.html)
- **PostgreSQL Documentation** : [https://www.postgresql.org/docs/](https://www.postgresql.org/docs/)

### 🐛 **Signaler un Problème**
- **GitHub Issues** : [https://github.com/loi200812/sama-etat/issues](https://github.com/loi200812/sama-etat/issues)
- **Étiquettes** : `dependencies`, `installation`, `bug`

---

**SAMA ÉTAT v1.3 Stable** - Dépendances Validées et Testées 🇸🇳
