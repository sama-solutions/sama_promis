# -*- coding: utf-8 -*-
{
    'name': 'SAMA PROMIS - Program Management Information System',
    'version': '18.0.4.0.1',  # Phase 4: Public & Requestor Portals
    'category': 'Project Management/Public Transparency',
    'summary': 'Program Management Information System - Micromodules Architecture (Phase 4: Portals)',
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
        
        Fonctionnalités Phase 1 - Gestion Multi-Sources:
        - Support de plusieurs sources de financement par projet
        - Classification automatique des fonds internationaux vs locaux
        - Gestion multi-devises avec conversion automatique
        - Traçabilité complète par bailleur et origine
        - Rétrocompatibilité avec les projets existants
        
        Fonctionnalités Phase 2 - Plans de Passation de Marché:
        - Gestion complète des plans de passation de marché
        - Suivi des méthodes de passation (appels d'offres, gré à gré, etc.)
        - Workflows simplifiés (brouillon → validé → en exécution → terminé)
        - Intégration avec projets et contrats
        - Suivi des coûts estimés vs réels
        - Jalons financiers et conformité de base
        
        Fonctionnalités Phase 3 - Conformité Bailleurs:
        - Profils de conformité par bailleur (BM, CE, AFD, etc.)
        - Gestion des tâches de conformité (jalons, livrables, rapports)
        - Rapports spécifiques par bailleur (QWeb templates)
        - Rappels automatiques et escalades (cron jobs)
        - Matrices de conformité et checklists
        - Suivi des échéances et taux de conformité
        - Intégration complète avec projets et contrats
        
        Fonctionnalités Phase 4 - Portails Public et Requérant:
        - Tableau de bord public de la transparence avec navigation moderne
        - Visualisation complète des fonds, projets, passation de marchés, appels à propositions
        - Design institutionnel inspiré de SAMA ETAT (minimaliste, propre, professionnel)
        - Portail requérant authentifié pour suivi des interactions
        - Gestion des propositions, contrats, conformité, paiements
        - Notifications et alertes personnalisées
        - Export de données et partage via QR codes
        - API JSON pour intégrations externes
    """,
    'author': 'SAMA Transparent State Solutions - Solutions Transparentes pour État, Mamadou Mbagnick DOGUE, Rassol DOGUE',
    'website': 'https://www.samaetat.sn',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'website',  # For public portal
        'portal',   # For requestor portal
        'mail',     # For notifications and chatter
        'project',
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
        'views/project_funding_source_views.xml',
        'views/call_for_proposal_views.xml',
        'views/contract_views.xml',
        'views/contract_template_views.xml',
        'views/res_partner_views.xml',
        'views/evaluation_views.xml',
        'views/payment_views.xml',
        'views/event_views.xml',
        'views/tag_views.xml',
        'views/procurement_plan_views.xml',
        'views/compliance_profile_views.xml',
        'views/compliance_task_views.xml',
        'views/menus.xml',
        
        # Reports
        'views/contract_report.xml',
        'reports/compliance_report_base.xml',
        'reports/compliance_report_worldbank.xml',
        'reports/compliance_report_eu.xml',
        'reports/compliance_report_afd.xml',
        
        # Public portal templates (Phase 4)
        'micromodules/public_portal/templates/promispublic.xml',
        'micromodules/public_portal/templates/citizen_portal.xml',
        
        # Data
        'data/base_data.xml',
        'data/project_type_data.xml',
        'data/sequences.xml',
        'data/compliance_cron.xml',
        'data/compliance_mail_templates.xml',
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
            'sama_promis/static/css/promispublic_modern.css',
            'sama_promis/static/js/promispublic_modern.js',
        ],
    },
    'test': [
        'tests/test_installation.py',
        'tests/test_models.py',
        'tests/test_payment.py',
        'tests/test_phase2_features.py',
        'tests/test_controllers.py',
        'tests/test_micromodules.py',
        # Public portal tests disabled - to be developed later
        # 'tests/test_public_portal.py',
        # 'tests/test_controller_routes.py',  # Not in manifest but exists
        'tests/test_qr_codes.py',
        'tests/test_workflows.py',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}