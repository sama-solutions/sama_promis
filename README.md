# SAMA ÉTAT – Plateforme citoyenne de gouvernance stratégique, opérationnelle et transparente

SAMA ÉTAT est une plateforme numérique open source conçue pour digitaliser intégralement la gouvernance publique vers le zéro-papier. Elle vise à structurer, piloter et rendre visible toute action publique, au service d’une République transparente, performante et inclusive.

## Une plateforme pensée pour résoudre un vrai problème public

Aujourd’hui, les projets gouvernementaux sont trop souvent dispersés, peu traçables, et inaccessibles aux citoyens. SAMA ÉTAT centralise l'information, connecte les décisions, aligne les parties prenantes et outille les citoyens.

Elle transforme l’État, non par promesse, mais par architecture logicielle.

## Ce que fait SAMA ÉTAT

*   Regroupe et structure tous les projets publics (nationaux, ministériels, territoriaux) sous une feuille de route unique.
*   Suit en temps réel les décisions du Président, du Premier Ministre, du Conseil des ministres et des ministres.
*   Connecte toute l’administration territoriale (maires, préfets, sous-préfets, gouverneurs).
*   Intègre un moteur de pilotage, d’exécution, de suivi-évaluation et d’observabilité des politiques publiques.
*   Rapproche le citoyen des projets, des budgets et des responsabilités.

## Les avantages pour chaque acteur

### Pour le gouvernement
### Pour le gouvernement

*   Un tableau de bord centralisé du Plan Sénégal 2050.
*   Un outil unique pour coordonner, contrôler et corriger les politiques publiques.
*   Carte interactive avec coordonnées GPS réalistes de tous les projets, décisions et événements.
*   Zéro coût de licence, 100% open source, 100% aligné avec les ODD.
*   Une plateforme nationale qui institutionnalise la reddition de comptes.

### Pour les citoyens

*   Accès libre à tous les projets publics en cours, localement et nationalement.
*   Visualisation géographique des initiatives gouvernementales dans leur région.
*   Suivi en temps réel de l'exécution, des retards, et des budgets.
*   Possibilité d'interpellation légitime et de participation active à la vie publique.
*   Une République qui rend des comptes, projet par projet.

### Pour les entreprises, ONG ou institutions

*   Un outil d’alignement sur les feuilles de route gouvernementales.
*   Réduction des doublons, meilleure coordination avec l’État.
*   Plateforme adaptée à tout plan stratégique ou portefeuille de projets, quelle que soit la taille.
*   Outil de reporting, de suivi contractuel et de transparence.

## Transparence par design

SAMA ÉTAT place la transparence au cœur de son fonctionnement. Chaque projet, chaque acteur, chaque ressource est visible, traçable et responsable.

La confiance ne se décrète pas. Elle se construit ligne par ligne, API par API, dans un écosystème fiable, neutre et opposable.

Le peuple a conçu l’outil. À l’État de l'adopter, aux institutions de l’intégrer, aux citoyens de l’utiliser.

Auteurs : Mamadou Mbagnick DOGUE, Rassol DOGUE

---

# SAMA ÉTAT – Citizen platform for strategic, operational, and transparent governance

SAMA ÉTAT is an open-source digital platform designed to fully digitize public governance towards zero-paper. It aims to structure, manage, and make visible all public actions, serving a transparent, efficient, and inclusive Republic.

## A platform designed to solve a real public problem

Today, government projects are too often dispersed, poorly traceable, and inaccessible to citizens. SAMA ÉTAT centralizes information, connects decisions, aligns stakeholders, and empowers citizens.

It transforms the State, not by promise, but by software architecture.

## What SAMA ÉTAT does

*   Groups and structures all public projects (national, ministerial, territorial) under a single roadmap.
*   Monitors in real-time the decisions of the President, the Prime Minister, the Council of Ministers, and the ministers.
*   Connects the entire territorial administration (mayors, prefects, sub-prefects, governors).
*   Integrates a motor for steering, execution, monitoring-evaluation, and observability of public policies.
*   Brings citizens closer to projects, budgets, and responsibilities.

## Advantages for each stakeholder

### For the government

*   A centralized dashboard for the Senegal 2050 Plan.
*   A unique tool to coordinate, control, and correct public policies.
*   Zero license cost, 100% open source, 100% aligned with SDGs.
*   A national platform that institutionalizes accountability.

### For citizens

*   Free access to all ongoing public projects, locally and nationally.
*   Interactive map showing government initiatives across all Senegalese regions.
*   Real-time monitoring of execution, delays, and budgets.
*   Possibility of legitimate questioning and active participation in public life.
*   A Republic that is accountable, project by project.

### For businesses, NGOs, or institutions

*   A tool for alignment with government roadmaps.
*   Reduction of redundancies, better coordination with the State.
*   Platform adaptable to any strategic plan or project portfolio, regardless of size.
*   Reporting, contractual monitoring, and transparency tool.

## Transparency by design

SAMA ÉTAT places transparency at the heart of its operation. Every project, every actor, every resource is visible, traceable, and accountable.

Trust is not decreed. It is built line by line, API by API, in a reliable, neutral, and enforceable ecosystem.

The people designed the tool. It is up to the State to adopt it, to institutions to integrate it, and to citizens to use it.

Authors: Mamadou Mbagnick DOGUE, Rassol DOGUE

---

## Installation Guide (English)

### Prerequisites

*   Docker and Docker Compose installed on your system.

### Docker Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/loi200812/sama-etat
    cd sama_etat
    ```
2.  **Create a `docker-compose.yml` file in the root of your project:**
    ```yaml
    version: '3.8'

    services:
      db:
        image: postgres:15
        environment:
          - POSTGRES_DB=odoo_db
          - POSTGRES_PASSWORD=odoo
          - POSTGRES_USER=odoo
        ports:
          - "5432:5432"
        volumes:
          - odoo-db-data:/var/lib/postgresql/data

      odoo:
        build:
          context: .
          dockerfile: Dockerfile
        ports:
          - "8069:8069"
          - "8071:8071"
        depends_on:
          - db
        environment:
          - HOST=db
          - USER=odoo
          - PASSWORD=odoo
        volumes:
          - odoo-web-data:/var/lib/odoo
          - ./custom_addons:/mnt/extra-addons
          - ./odoo.conf:/etc/odoo/odoo.conf
        command: --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons -c /etc/odoo/odoo.conf

    volumes:
      odoo-db-data:
      odoo-web-data:
    ```
3.  **Create a `Dockerfile` in the root of your project:**
    ```dockerfile
    FROM odoo:18.0

    # Install Python dependencies
    RUN pip install qrcode pillow

    # Copy custom addons
    COPY ./custom_addons /mnt/extra-addons

    # Copy odoo.conf
    COPY ./odoo.conf /etc/odoo/odoo.conf

    # Expose Odoo port
    EXPOSE 8069
    EXPOSE 8071

    # Set default command to run Odoo
    CMD ["odoo"]
    ```
4.  **Build and run the Docker containers:**
    ```bash
    docker-compose up --build -d
    ```
5.  **Access Odoo:**
    Open your web browser and go to `http://localhost:8069`.

### Manual Installation (Linux/Ubuntu)

1.  **Install PostgreSQL:**
    ```bash
    sudo apt update
    sudo apt install postgresql -y
    sudo -u postgres createuser --superuser odoo
    ```
2.  **Install Python and dependencies:**
    ```bash
    sudo apt install python3 python3-pip python3-dev build-essential libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libssl-dev -y
    pip3 install -r requirements.txt # You'll need to create a requirements.txt with qrcode and pillow
    ```
3.  **Clone Odoo 18.0:**
    ```bash
    git clone https://www.github.com/odoo/odoo --depth 1 --branch 18.0 /opt/odoo18
    ```
4.  **Clone SAMA ÉTAT module:**
    ```bash
    git clone https://github.com/loi200812/sama-etat /opt/odoo18/custom_addons/sama_etat
    ```
5.  **Configure Odoo:**
    Create an Odoo configuration file (e.g., `/etc/odoo/odoo.conf`):
    ```ini
    [options]
    addons_path = /opt/odoo18/addons,/opt/odoo18/custom_addons
    data_dir = /var/lib/odoo
    admin_passwd = admin
    db_host = False
    db_port = False
    db_user = odoo
    db_password = odoo
    xmlrpc_port = 8069
    longpolling_port = 8071
    logfile = /var/log/odoo/odoo.log
    log_level = info
    ```
    Create log directory and set permissions:
    ```bash
    sudo mkdir /var/log/odoo
    sudo chown odoo:odoo /var/log/odoo
    ```
6.  **Start Odoo:**
    ```bash
    /opt/odoo18/odoo-bin -c /etc/odoo/odoo.conf
    ```
    For background process:
    ```bash
    nohup /opt/odoo18/odoo-bin -c /etc/odoo/odoo.conf &
    ```
7.  **Access Odoo:**
    Open your web browser and go to `http://localhost:8069`.

---

## Guide d'Installation (Français)

### Prérequis

*   Docker et Docker Compose installés sur votre système.

### Installation Docker

1.  **Cloner le dépôt :**
    ```bash
    git clone https://github.com/loi200812/sama-etat
    cd sama_etat
    ```
2.  **Créer un fichier `docker-compose.yml` à la racine de votre projet :**
    ```yaml
    version: '3.8'

    services:
      db:
        image: postgres:15
        environment:
          - POSTGRES_DB=odoo_db
          - POSTGRES_PASSWORD=odoo
          - POSTGRES_USER=odoo
        ports:
          - "5432:5432"
        volumes:
          - odoo-db-data:/var/lib/postgresql/data

      odoo:
        build:
          context: .
          dockerfile: Dockerfile
        ports:
          - "8069:8069"
          - "8071:8071"
        depends_on:
          - db
        environment:
          - HOST=db
          - USER=odoo
          - PASSWORD=odoo
        volumes:
          - odoo-web-data:/var/lib/odoo
          - ./custom_addons:/mnt/extra-addons
          - ./odoo.conf:/etc/odoo/odoo.conf
        command: --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons -c /etc/odoo/odoo.conf

    volumes:
      odoo-db-data:
      odoo-web-data:
    ```
3.  **Créer un fichier `Dockerfile` à la racine de votre projet :**
    ```dockerfile
    FROM odoo:18.0

    # Installer les dépendances Python
    RUN pip install qrcode pillow

    # Copier les modules personnalisés
    COPY ./custom_addons /mnt/extra-addons

    # Copier odoo.conf
    COPY ./odoo.conf /etc/odoo/odoo.conf

    # Exposer le port Odoo
    EXPOSE 8069
    EXPOSE 8071

    # Définir la commande par défaut pour lancer Odoo
    CMD ["odoo"]
    ```
4.  **Construire et lancer les conteneurs Docker :**
    ```bash
    docker-compose up --build -d
    ```
5.  **Accéder à Odoo :**
    Ouvrez votre navigateur web et accédez à `http://localhost:8069`.

### Installation Manuelle (Linux/Ubuntu)

1.  **Installer PostgreSQL :**
    ```bash
    sudo apt update
    sudo apt install postgresql -y
    sudo -u postgres createuser --superuser odoo
    ```
2.  **Installer Python et les dépendances :**
    ```bash
    sudo apt install python3 python3-pip python3-dev build-essential libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libssl-dev -y
    pip3 install -r requirements.txt # Vous devrez créer un fichier requirements.txt avec qrcode et pillow
    ```
3.  **Cloner Odoo 18.0 :**
    ```bash
    git clone https://www.github.com/odoo/odoo --depth 1 --branch 18.0 /opt/odoo18
    ```
4.  **Cloner le module SAMA ÉTAT :**
    ```bash
    git clone https://github.com/loi200812/sama-etat /opt/odoo18/custom_addons/sama_etat
    ```
5.  **Configurer Odoo :**
    Créer un fichier de configuration Odoo (par exemple, `/etc/odoo/odoo.conf`) :
    ```ini
    [options]
    addons_path = /opt/odoo18/addons,/opt/odoo18/custom_addons
    data_dir = /var/lib/odoo
    admin_passwd = admin
    db_host = False
    db_port = False
    db_user = odoo
    db_password = odoo
    xmlrpc_port = 8069
    longpolling_port = 8071
    logfile = /var/log/odoo/odoo.log
    log_level = info
    ```
    Créer le répertoire de logs et définir les permissions :
    ```bash
    sudo mkdir /var/log/odoo
    sudo chown odoo:odoo /var/log/odoo
    ```
6.  **Lancer Odoo :**
    ```bash
    /opt/odoo18/odoo-bin -c /etc/odoo/odoo.conf
    ```
    Pour un processus en arrière-plan :
    ```bash
    nohup /opt/odoo18/odoo-bin -c /etc/odoo/odoo.conf &
    ```
7.  **Accéder à Odoo :**
    Ouvrez votre navigateur web et accédez à `http://localhost:8069`.