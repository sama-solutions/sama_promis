{
    'name': 'SAMA ETAT',
    'version': '1.0',
    'category': 'Project Management',
    'summary': 'Module for managing government projects, decisions, events, and budgets based on Plan Senegal 2050.',
    'description': """
        This module provides a comprehensive solution for managing various aspects of government operations
        in Senegal, aligning them with the strategic objectives of Plan Senegal 2050.
    """,
    'author': 'Your Name/Organization', # TODO: Replace with actual author
    'website': 'http://www.yourwebsite.com', # TODO: Replace with actual website
    'depends': ['base', 'project', 'mail', 'website', 'hr', 'calendar', 'website_event'],
    'data': [
        # Security files loaded first to ensure groups are defined
        'security/security.xml',
        'security/ir.model.access.csv',
        # Views defining actions and structures must be loaded after security
        'views/views.xml',
        'views/strategic_plan_views.xml',
        'views/strategic_pillar_views.xml',
        'views/strategic_axis_views.xml',
        'views/strategic_objective_views.xml',
        'views/strategic_kpi_views.xml',
        'views/government_project_views.xml',
        'views/government_decision_views.xml',
        'views/government_event_views.xml',
        'views/government_budget_views.xml',
        'views/government_ministry_views.xml',


        'views/public_templates.xml',
        'views/public_templates_extra.xml',
        'views/public_templates_modern.xml',
        'views/modern_dashboard.xml',
        'views/public_decision_page.xml',
        'views/public_event_page.xml',
        'views/public_objective_page.xml',
        'views/public_axis_page.xml',
        'views/public_pillar_page.xml',
        'views/calendar_event_views.xml',
        # Wizard views
        'wizard/government_project_wizard_views.xml',
        # Menu views loaded after all actions
        'views/dashboard_views.xml',
        'views/public_map.xml',
        'views/fullscreen_map.xml',
        'views/website_homepage.xml',
        'views/website_about.xml',
        # Currency configuration
        'data/currency_xof_data.xml',
        # Demo data files
        'data/strategic_objectives_demo_data.xml',
        'data/ministries_demo_data.xml',
        'data/budgets_demo_data.xml',
        'data/government_projects_demo_data.xml',
        'data/employees_demo_data.xml',
        'data/project_tasks_demo_data.xml',
        'data/government_events_demo_data.xml',
        'data/government_decisions_demo_data.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': ['qrcode', 'pillow']
    },
}
