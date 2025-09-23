# -*- coding: utf-8 -*-
{
    'name': 'SAMA PROMIS - Program Management Information System',
    'version': '18.0.3.0.0',
    'category': 'Project Management',
    'summary': 'Program Management Information System - Micromodules Architecture',
    'description': """
        SAMA PROMIS - Program Management Information System
        ================================================

        Architecture micromodules pour la gestion des projets de bailleurs de fonds internationaux.
        
        Micromodules inclus:
        - Core: Modèles de base, QR codes, workflows, audit
        - Projects: Gestion des projets avec cycles de vie
        - Public Portal: Dashboard "PROMISPUBLIC" et page citoyenne
        - Calls: Appels à propositions
        - Contracts: Contrats et signatures électroniques
        - Payments: Gestion des paiements
        - Evaluations: Évaluations et indicateurs
        
        Fonctionnalités:
        - Cycles de vie complets avec boutons d'action (inspiré SAMA ETAT)
        - QR codes automatiques pour tous les modèles
        - Dashboard public moderne avec cartes et filtres
        - Page citoyenne "SAMA PROMIS ET MOI"
        - Architecture résiliente et modulaire
    """,
    'author': 'SAMA Transparent State Solutions - Solutions Transparentes pour État, Mamadou Mbagnick DOGUE, Rassol DOGUE',
    'website': 'https://www.samaetat.sn',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'website',  # For public portal
        'mail',     # For notifications and chatter
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/sama_promis_security.xml',
        
        # Views
        'views/project_views.xml',
        'views/tag_views.xml',
        
        # Templates
        'templates/promispublic.xml',
        'templates/citizen_portal.xml',
        
        # Data
        'data/base_data.xml',
        
        # Menus
        'views/menus.xml',
    ],
    'demo': [],
    'assets': {
        'web.assets_frontend': [
            'sama_promis/static/css/promispublic.css',
            'sama_promis/static/js/promispublic.js',
        ],
    },
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}