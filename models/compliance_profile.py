# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SamaPromisComplianceProfile(models.Model):
    """Profil de Conformité Bailleur - Stores donor-specific compliance requirements."""
    
    _name = 'sama.promis.compliance.profile'
    _description = 'Profil de Conformité Bailleur'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    
    # Core Fields
    name = fields.Char(
        string='Nom du Profil',
        required=True,
        tracking=True,
        help="Nom du profil de conformité (ex: 'World Bank Standard Compliance')"
    )
    code = fields.Char(
        string='Code',
        required=True,
        help="Code court unique (ex: 'WB_STD', 'EU_H2020', 'AFD_CONV')"
    )
    description = fields.Html(
        string='Description',
        help="Description détaillée des exigences de conformité"
    )
    donor_ids = fields.Many2many(
        'res.partner',
        'compliance_profile_donor_rel',
        'profile_id',
        'donor_id',
        string='Bailleurs',
        domain=[('is_donor', '=', True)],
        help="Bailleurs utilisant ce profil de conformité"
    )
    is_active = fields.Boolean(
        string='Actif',
        default=True,
        help="Indique si ce profil est actif"
    )
    
    # Reporting Requirements
    reporting_frequency = fields.Selection([
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('semi_annual', 'Semestriel'),
        ('annual', 'Annuel'),
        ('custom', 'Personnalisé')
    ], string='Fréquence de Rapportage', required=True, default='quarterly',
        help="Fréquence de soumission des rapports de conformité")
    
    custom_frequency_days = fields.Integer(
        string='Fréquence Personnalisée (jours)',
        help="Nombre de jours pour la fréquence personnalisée"
    )
    report_template_id = fields.Many2one(
        'ir.actions.report',
        string='Modèle de Rapport',
        help="Modèle QWeb à utiliser pour générer les rapports"
    )
    report_format = fields.Selection([
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('both', 'PDF et Excel')
    ], string='Format de Rapport', default='pdf')
    
    requires_financial_report = fields.Boolean(
        string='Rapport Financier Requis',
        default=True,
        help="Indique si un rapport financier est requis"
    )
    requires_narrative_report = fields.Boolean(
        string='Rapport Narratif Requis',
        default=True,
        help="Indique si un rapport narratif/de progrès est requis"
    )
    requires_indicator_report = fields.Boolean(
        string='Rapport d\'Indicateurs Requis',
        default=True,
        help="Indique si un rapport d'indicateurs/résultats est requis"
    )
    
    # Compliance Matrix Fields
    compliance_checklist = fields.Text(
        string='Checklist de Conformité',
        help="Liste des éléments de conformité au format JSON"
    )
    mandatory_documents = fields.Text(
        string='Documents Obligatoires',
        help="Liste des documents obligatoires au format JSON"
    )
    approval_workflow = fields.Selection([
        ('single', 'Approbation Simple'),
        ('dual', 'Double Approbation'),
        ('committee', 'Comité')
    ], string='Workflow d\'Approbation', default='single',
        help="Type de workflow d'approbation requis")
    
    prior_review_threshold = fields.Monetary(
        string='Seuil de Revue Préalable',
        currency_field='currency_id',
        help="Montant nécessitant une revue préalable du bailleur"
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    
    # Notification Settings
    reminder_days_before = fields.Integer(
        string='Rappel (jours avant)',
        default=7,
        help="Nombre de jours avant l'échéance pour envoyer un rappel"
    )
    escalation_days_after = fields.Integer(
        string='Escalade (jours après)',
        default=3,
        help="Nombre de jours après l'échéance pour escalader"
    )
    notification_user_ids = fields.Many2many(
        'res.users',
        'compliance_profile_notification_user_rel',
        'profile_id',
        'user_id',
        string='Utilisateurs à Notifier',
        help="Utilisateurs à notifier pour les problèmes de conformité"
    )
    
    # Statistics
    project_count = fields.Integer(
        string='Nombre de Projets',
        compute='_compute_statistics',
        store=True,
        help="Nombre de projets utilisant ce profil"
    )
    contract_count = fields.Integer(
        string='Nombre de Contrats',
        compute='_compute_statistics',
        store=True,
        help="Nombre de contrats utilisant ce profil"
    )
    compliance_rate = fields.Float(
        string='Taux de Conformité',
        compute='_compute_statistics',
        store=True,
        help="Taux de conformité global en pourcentage"
    )
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Le code du profil de conformité doit être unique!'),
        ('check_custom_frequency', 
         "CHECK(reporting_frequency != 'custom' OR custom_frequency_days > 0)",
         'La fréquence personnalisée doit être supérieure à 0 jours!'),
        ('check_threshold_positive',
         'CHECK(prior_review_threshold >= 0)',
         'Le seuil de revue préalable doit être positif ou nul!')
    ]
    
    @api.depends('donor_ids')
    def _compute_statistics(self):
        """Calculate statistics for projects and contracts using this profile."""
        for profile in self:
            # Count projects using this profile
            projects = self.env['sama.promis.project'].search([
                ('compliance_profile_id', '=', profile.id)
            ])
            profile.project_count = len(projects)
            
            # Count contracts using this profile
            contracts = self.env['sama.promis.contract'].search([
                ('compliance_profile_id', '=', profile.id)
            ])
            profile.contract_count = len(contracts)
            
            # Calculate overall compliance rate
            if projects:
                total_rate = sum(projects.mapped('compliance_rate'))
                profile.compliance_rate = total_rate / len(projects) if projects else 0.0
            else:
                profile.compliance_rate = 0.0
    
    def calculate_next_report_date(self, start_date):
        """Calculate the next report date based on reporting frequency.
        
        Args:
            start_date: The starting date (last report date or project start date)
            
        Returns:
            date: The next report due date
        """
        self.ensure_one()
        from dateutil.relativedelta import relativedelta
        from datetime import timedelta
        
        if not start_date:
            return False
            
        if self.reporting_frequency == 'monthly':
            return start_date + relativedelta(months=1)
        elif self.reporting_frequency == 'quarterly':
            return start_date + relativedelta(months=3)
        elif self.reporting_frequency == 'semi_annual':
            return start_date + relativedelta(months=6)
        elif self.reporting_frequency == 'annual':
            return start_date + relativedelta(years=1)
        elif self.reporting_frequency == 'custom' and self.custom_frequency_days:
            return start_date + timedelta(days=self.custom_frequency_days)
        
        return False
    
    def get_compliance_checklist_items(self):
        """Parse compliance_checklist JSON and return list of items.
        
        Returns:
            list: List of checklist items
        """
        self.ensure_one()
        import json
        
        if not self.compliance_checklist:
            return []
        
        try:
            return json.loads(self.compliance_checklist)
        except (json.JSONDecodeError, ValueError):
            return []
    
    def get_mandatory_documents_list(self):
        """Parse mandatory_documents JSON and return list.
        
        Returns:
            list: List of mandatory documents
        """
        self.ensure_one()
        import json
        
        if not self.mandatory_documents:
            return []
        
        try:
            return json.loads(self.mandatory_documents)
        except (json.JSONDecodeError, ValueError):
            return []
    
    def action_view_projects(self):
        """Open projects using this compliance profile."""
        self.ensure_one()
        return {
            'name': _('Projets - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'sama.promis.project',
            'view_mode': 'tree,form',
            'domain': [('compliance_profile_id', '=', self.id)],
            'context': {'default_compliance_profile_id': self.id}
        }
    
    def action_view_contracts(self):
        """Open contracts using this compliance profile."""
        self.ensure_one()
        return {
            'name': _('Contrats - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'sama.promis.contract',
            'view_mode': 'tree,form',
            'domain': [('compliance_profile_id', '=', self.id)],
            'context': {}
        }
