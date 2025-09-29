# -*- coding: utf-8 -*-
{
    'name': 'SAMA PROMIS - Program Management Information System',
    'version': '18.0.3.1.0',  # Version hybride
    'category': 'Project Management',
    'summary': 'Program Management Information System - Micromodules Architecture (Version Hybride)',
    'description': """
        SAMA PROMIS - Program Management Information System
        ================================================

        Architecture micromodules pour la gestion des projets de bailleurs de fonds internationaux.
        Version hybride combinant les fonctionnalités avancées et les améliorations.
        
        Micromodules inclus:
        - Core: Modèles de base, QR codes, workflows, audit
        - Projects: Gestion des projets avec cycles de vie
        - Public Portal: Dashboard "PROMISPUBLIC" et page citoyenne
        - Calls: Appels à propositions
        - Contracts: Contrats et signatures électroniques (améliorés)
        - Payments: Gestion des paiements
        - Evaluations: Évaluations et indicateurs
        
        Fonctionnalités:
        - Cycles de vie complets avec boutons d'action (inspiré SAMA ETAT)
        - QR codes automatiques pour tous les modèles
        - Dashboard public moderne avec cartes et filtres
        - Page citoyenne "SAMA PROMIS ET MOI"
        - Modèles de contrats avancés avec aperçu
        - Architecture résiliente et modulaire
    """,
    'author': 'SAMA Transparent State Solutions - Solutions Transparentes pour État, Mamadou Mbagnick DOGUE, Rassol DOGUE',
    'website': 'https://www.samaetat.sn',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'website',  # For public portal
        'mail',     # For notifications and chatter
        'project',
        'account',
    ],
    'external_dependencies': {
        'python': ['qrcode'],
    },
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/sama_promis_security.xml',
        
        # Views
        'views/project_views.xml',
        'views/call_for_proposal_views.xml',
        'views/contract_views.xml',
        'views/contract_template_views.xml',  # Nouveau: vues contract_template
        'views/res_partner_views.xml',
        'views/evaluation_views.xml',
        'views/payment_views.xml',
        'views/event_views.xml',
        'views/tag_views.xml',
        
        'templates/promispublic.xml',
        'templates/citizen_portal.xml',
        
        # Data
        'data/base_data.xml',
        'data/project_type_data.xml',
        'data/sequences.xml',
        'demo/enhanced_demo_data.xml',
    ],
    'demo': [
        'demo/project_demo.xml',
        'demo/contract_demo.xml',
        'demo/payment_demo.xml',
        'demo/partner_demo.xml',
        'demo/enhanced_demo_data.xml',  # Données enrichies supplémentaires
    ],
    'assets': {
        'web.assets_frontend': [
            'sama_promis/static/css/promispublic.css',
        ],
    },
    'test': [
        'tests/test_installation.py',
        'tests/test_models.py',
        'tests/test_payment.py',
        'tests/test_phase2_features.py',
        'tests/test_controllers.py',
        'tests/test_micromodules.py',
        'tests/test_public_portal.py',
        'tests/test_qr_codes.py',
        'tests/test_workflows.py',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}