{
    'name': 'Gestion des Projets Publics - Sénégal',
    'version': '18.0.1.0.0',
    'category': 'Project',
    'summary': 'Module de gestion des projets publics au Sénégal',
    'description': """
Module de gestion des projets publics au Sénégal
================================================

Ce module permet de gérer les projets publics au Sénégal avec les fonctionnalités suivantes :

* Gestion des projets publics avec informations détaillées
* Suivi des budgets et sources de financement
* Gestion des risques et indicateurs
* Localisation par département et commune
* Gestion des partenaires et marchés publics
* Secteurs d'intervention et politiques publiques
    """,
    'author': 'Votre Nom',
    'website': 'https://www.example.com',
    'depends': ['base', 'mail', 'contacts'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        # Charger les vues des modèles de configuration AVANT la vue principale qui les utilise
        'views/project_public_sector_view.xml',
        'views/project_public_policy_view.xml',
        'views/project_public_info_type_view.xml',
        'views/project_public_location_view.xml',
        # Charger la vue principale du projet en dernier
        'views/project_public_project_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}

