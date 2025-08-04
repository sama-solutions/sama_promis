# 🚀 Guide d'Installation SAMA ÉTAT v1.3 Stable

## 📋 Vue d'ensemble

SAMA ÉTAT v1.3 apporte des fonctionnalités majeures incluant une **carte interactive complète** et un **workflow des événements gouvernementaux** avec création automatique d'événements Odoo.

## 🎯 Nouvelles Fonctionnalités v1.3

### 🗺️ **Carte Interactive**
- Visualisation plein écran avec géolocalisation GPS
- Filtrage par projets, décisions, événements
- Clustering intelligent des marqueurs
- Interface responsive et moderne

### 📅 **Workflow Événements**
- Cycle complet : Brouillon → Validé → En cours → Terminé
- Création automatique d'événements Odoo
- Double accès : Profil public + Gestion administrative

## 📦 Prérequis Système

### 🖥️ **Serveur**
```bash
# Système d'exploitation
Ubuntu 20.04+ LTS ou Debian 11+

# Ressources minimales
- RAM: 4GB (8GB recommandé)
- CPU: 2 cores (4 cores recommandé)
- Stockage: 20GB (50GB recommandé)
- Réseau: Connexion internet stable
```

### 🐍 **Logiciels Requis**
```bash
# Python 3.8+
python3 --version

# PostgreSQL 12+
psql --version

# Git
git --version

# Node.js 16+ (optionnel, pour développement)
node --version
```

## 🔧 Installation Complète

### 1️⃣ **Préparation du Système**

```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances système
sudo apt install -y python3-pip python3-dev python3-venv
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y git curl wget
sudo apt install -y build-essential libssl-dev libffi-dev
sudo apt install -y libjpeg-dev libpng-dev libfreetype6-dev
sudo apt install -y libxml2-dev libxslt1-dev zlib1g-dev
```

### 2️⃣ **Installation PostgreSQL**

```bash
# Démarrage du service PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Configuration utilisateur PostgreSQL
sudo -u postgres createuser -s $USER
sudo -u postgres createdb $USER

# Création base de données pour Odoo
createdb sama_etat_db
```

### 3️⃣ **Installation Odoo 18**

```bash
# Téléchargement Odoo 18
cd /opt
sudo git clone https://github.com/odoo/odoo.git --depth 1 --branch 18.0 odoo18
sudo chown -R $USER:$USER odoo18

# Installation dépendances Python
cd odoo18
pip3 install -r requirements.txt

# Dépendances supplémentaires pour SAMA ÉTAT
pip3 install qrcode[pil] pillow geopy
```

### 4️⃣ **Installation SAMA ÉTAT v1.3**

```bash
# Clonage du repository
cd /opt
git clone https://github.com/loi200812/sama-etat.git
cd sama-etat

# Vérification de la version
git checkout v1.3-stable

# Copie dans les addons Odoo
mkdir -p /opt/odoo18/custom_addons
cp -r sama_etat /opt/odoo18/custom_addons/

# Permissions
sudo chown -R $USER:$USER /opt/odoo18/custom_addons
```

### 5️⃣ **Configuration Odoo**

```bash
# Création fichier de configuration
cat > /opt/odoo18/odoo.conf << 'EOF'
[options]
# Serveur
http_port = 8069
db_host = localhost
db_port = 5432
db_user = $USER
db_password = False

# Addons
addons_path = /opt/odoo18/addons,/opt/odoo18/custom_addons

# Logs
logfile = /var/log/odoo/odoo.log
log_level = info

# Performance
workers = 2
max_cron_threads = 1
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200

# Sécurité
admin_passwd = your_master_password_here
list_db = False
EOF

# Création répertoire logs
sudo mkdir -p /var/log/odoo
sudo chown $USER:$USER /var/log/odoo
```

### 6️⃣ **Premier Démarrage**

```bash
# Démarrage Odoo avec SAMA ÉTAT
cd /opt/odoo18
python3 odoo-bin -c odoo.conf -d sama_etat_db -i sama_etat --stop-after-init

# Démarrage normal
python3 odoo-bin -c odoo.conf
```

## 🌐 Accès à l'Application

### 📱 **Interface Web**
```
URL: http://localhost:8069
Base de données: sama_etat_db
Utilisateur: admin
Mot de passe: admin (à changer)
```

### 🗺️ **Carte Interactive**
```
URL: http://localhost:8069/senegal2050/fullscreen_map
Accès: Public (pas de connexion requise)
```

### 📊 **Tableau de Bord Public**
```
URL: http://localhost:8069/senegal2050/dashboard
Accès: Public
```

## 🔄 Migration depuis v1.2

### 📋 **Sauvegarde Préalable**
```bash
# Sauvegarde base de données
pg_dump -U $USER sama_etat_db > backup_v1.2_$(date +%Y%m%d).sql

# Sauvegarde fichiers
tar -czf sama_etat_v1.2_backup.tar.gz /opt/odoo18/custom_addons/sama_etat
```

### 🔄 **Mise à Jour**
```bash
# Mise à jour du code
cd /opt/sama-etat
git fetch origin
git checkout v1.3-stable

# Copie nouvelle version
cp -r sama_etat /opt/odoo18/custom_addons/

# Mise à jour module dans Odoo
cd /opt/odoo18
python3 odoo-bin -c odoo.conf -d sama_etat_db -u sama_etat --stop-after-init
```

## 🔧 Configuration Avancée

### 🗺️ **Configuration Carte Interactive**

```python
# Dans les paramètres système Odoo
# Aller à : Paramètres > Paramètres Techniques > Paramètres Système

# Ajouter les paramètres suivants :
sama_etat.map_center_lat = 14.6928    # Latitude Dakar
sama_etat.map_center_lng = -17.4467   # Longitude Dakar
sama_etat.map_zoom_level = 7          # Niveau de zoom initial
sama_etat.map_cluster_radius = 50     # Rayon clustering
```

### 📧 **Configuration Email (Optionnel)**
```bash
# Dans odoo.conf, ajouter :
[options]
# ... autres paramètres ...

# Email
email_from = noreply@sama-etat.sn
smtp_server = smtp.gmail.com
smtp_port = 587
smtp_user = your-email@gmail.com
smtp_password = your-app-password
smtp_ssl = True
```

### 🔐 **Configuration HTTPS (Production)**
```nginx
# Configuration Nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://127.0.0.1:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

## 🐳 Installation avec Docker

### 📦 **Docker Compose**
```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: sama_etat
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  odoo:
    image: odoo:18
    depends_on:
      - postgres
    ports:
      - "8069:8069"
    environment:
      HOST: postgres
      USER: odoo
      PASSWORD: odoo_password
    volumes:
      - ./sama_etat:/mnt/extra-addons/sama_etat
      - odoo_data:/var/lib/odoo
    command: odoo -i sama_etat

volumes:
  postgres_data:
  odoo_data:
```

### 🚀 **Démarrage Docker**
```bash
# Clonage et démarrage
git clone https://github.com/loi200812/sama-etat.git
cd sama-etat
docker-compose up -d

# Vérification
docker-compose logs -f odoo
```

## 🧪 Tests et Validation

### ✅ **Tests Fonctionnels**
```bash
# Test de la carte interactive
curl -I http://localhost:8069/senegal2050/fullscreen_map

# Test API données carte
curl http://localhost:8069/sama_etat/get_map_data

# Test tableau de bord
curl -I http://localhost:8069/senegal2050/dashboard
```

### 🔍 **Vérification Installation**
1. **Connexion Odoo** : Interface admin accessible
2. **Module SAMA ÉTAT** : Installé et actif
3. **Carte interactive** : Affichage correct avec marqueurs
4. **Workflow événements** : Boutons de validation fonctionnels
5. **Pages publiques** : Accessibles sans connexion

## 🚨 Dépannage

### ❌ **Problèmes Courants**

#### **Erreur : Module non trouvé**
```bash
# Vérifier le chemin des addons
ls -la /opt/odoo18/custom_addons/sama_etat

# Vérifier la configuration
grep addons_path /opt/odoo18/odoo.conf
```

#### **Erreur : Carte ne s'affiche pas**
```bash
# Vérifier les logs
tail -f /var/log/odoo/odoo.log

# Vérifier les permissions
sudo chown -R $USER:$USER /opt/odoo18/custom_addons
```

#### **Erreur : Base de données**
```bash
# Recréer la base
dropdb sama_etat_db
createdb sama_etat_db

# Réinstaller le module
python3 odoo-bin -c odoo.conf -d sama_etat_db -i sama_etat --stop-after-init
```

### 📞 **Support**
- **GitHub Issues** : [https://github.com/loi200812/sama-etat/issues](https://github.com/loi200812/sama-etat/issues)
- **Documentation** : [README.md](README.md)
- **Changelog** : [CHANGELOG_v1.3.md](CHANGELOG_v1.3.md)

## 🎉 Installation Terminée !

Votre installation SAMA ÉTAT v1.3 est maintenant prête avec :
- ✅ Carte interactive fonctionnelle
- ✅ Workflow des événements opérationnel
- ✅ Interface publique accessible
- ✅ Administration Odoo configurée

**Accédez à votre plateforme :** `http://localhost:8069/senegal2050/dashboard`

---

**SAMA ÉTAT v1.3 Stable** - Une République Transparente, Projet par Projet 🇸🇳
