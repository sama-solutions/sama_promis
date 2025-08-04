from odoo import models, fields, api
from datetime import datetime, timedelta

class SenegalPlanDashboard(models.Model):
    """Modèle singleton pour le tableau de bord du Plan Sénégal 2050"""
    _name = 'senegal.plan.dashboard'
    _description = 'Tableau de Bord Plan Sénégal 2050'
    
    @api.model
    def get_dashboard(self):
        """Récupère ou crée l'unique instance du dashboard"""
        dashboard = self.search([], limit=1)
        if not dashboard:
            dashboard = self.create({})
        # Force recompute of all fields by updating a dummy field
        dashboard.write({'last_update_date': fields.Datetime.now()})
        return dashboard
    
    def default_get(self, fields):
        """Valeurs par défaut pour le dashboard"""
        result = super().default_get(fields)
        return result

    last_update_date = fields.Datetime(string="Dernière Mise à Jour", readonly=True)

    # Statistiques des projets
    total_projects = fields.Integer(string="Total des Projets", compute='_compute_project_stats')
    active_projects = fields.Integer(string="Projets Actifs", compute='_compute_project_stats')
    completed_projects = fields.Integer(string="Projets Achevés", compute='_compute_project_stats')
    suspended_projects = fields.Integer(string="Projets Suspendus", compute='_compute_project_stats')
    
    # Statistiques des ministères
    total_ministries = fields.Integer(string="Total des Ministères", compute='_compute_ministry_stats')
    active_ministries = fields.Integer(string="Ministères Actifs", compute='_compute_ministry_stats')
    
    # Statistiques budgétaires
    total_budget = fields.Monetary(string="Budget Total Alloué", currency_field='currency_id', compute='_compute_budget_stats')
    used_budget = fields.Monetary(string="Budget Utilisé", currency_field='currency_id', compute='_compute_budget_stats')
    remaining_budget = fields.Monetary(string="Budget Restant", currency_field='currency_id', compute='_compute_budget_stats')
    currency_id = fields.Many2one('res.currency', string='Devise')

    @api.model
    def _get_default_currency(self):
        """Obtenir la devise XOF par défaut"""
        try:
            return self.env['res.currency'].search([('name', '=', 'XOF')], limit=1)
        except:
            # Fallback to company currency if XOF not found
            return self.env.company.currency_id
    
    # Statistiques des objectifs stratégiques
    total_objectives = fields.Integer(string="Objectifs Stratégiques", compute='_compute_objective_stats')
    objectives_with_projects = fields.Integer(string="Objectifs avec Projets", compute='_compute_objective_stats')
    
    # Statistiques des décisions
    total_decisions = fields.Integer(string="Total des Décisions", compute='_compute_decision_stats')
    published_decisions = fields.Integer(string="Décisions Publiées", compute='_compute_decision_stats')
    
    # Statistiques des événements
    total_events = fields.Integer(string="Total des Événements", compute='_compute_event_stats')
    upcoming_events = fields.Integer(string="Événements à Venir", compute='_compute_event_stats')
    
    # Avancement global
    global_progress = fields.Float(string="Avancement Global (%)", compute='_compute_global_progress')
    
    @api.depends()
    def _compute_project_stats(self):
        for record in self:
            projects = self.env['government.project'].search([])
            record.total_projects = len(projects)
            record.active_projects = len(projects.filtered(lambda p: p.status in ['validated', 'in_progress']))
            record.completed_projects = len(projects.filtered(lambda p: p.status == 'completed'))
            record.suspended_projects = len(projects.filtered(lambda p: p.status == 'suspended'))
    
    @api.depends()
    def _compute_ministry_stats(self):
        for record in self:
            ministries = self.env['government.ministry'].search([])
            record.total_ministries = len(ministries)
            record.active_ministries = len(ministries.filtered(lambda m: m.project_count > 0))
    
    @api.depends()
    def _compute_budget_stats(self):
        for record in self:
            budgets = self.env['government.budget'].search([('status', '=', 'active')])
            record.total_budget = sum(budgets.mapped('allocated_amount'))
            record.used_budget = sum(budgets.mapped('used_amount'))
            record.remaining_budget = record.total_budget - record.used_budget
    
    @api.depends()
    def _compute_objective_stats(self):
        for record in self:
            objectives = self.env['strategic.objective'].search([])
            record.total_objectives = len(objectives)
            record.objectives_with_projects = len(objectives.filtered(lambda o: len(o.linked_projects) > 0))
    
    @api.depends()
    def _compute_decision_stats(self):
        for record in self:
            decisions = self.env['government.decision'].search([])
            record.total_decisions = len(decisions)
            record.published_decisions = len(decisions.filtered(lambda d: d.status == 'published'))
    
    @api.depends()
    def _compute_event_stats(self):
        for record in self:
            events = self.env['government.event'].search([])
            record.total_events = len(events)
            
            # Événements à venir (dans les 30 prochains jours)
            today = fields.Date.today()
            future_date = today + timedelta(days=30)
            upcoming_events = events.filtered(
                lambda e: e.event_date and e.event_date >= today and e.event_date <= future_date and e.status == 'planned'
            )
            record.upcoming_events = len(upcoming_events)
    
    @api.depends()
    def _compute_global_progress(self):
        for record in self:
            projects = self.env['government.project'].search([])
            if projects:
                total_progress = sum(projects.mapped('progress'))
                record.global_progress = total_progress / len(projects)
            else:
                record.global_progress = 0.0
    
    def action_view_projects(self):
        """Action pour voir tous les projets"""
        return self.env.ref('sama_etat.government_project_action').read()[0]
    
    def action_view_active_projects(self):
        """Action pour voir les projets actifs"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Projets Actifs',
            'res_model': 'government.project',
            'view_mode': 'list,form,kanban',
            'views': [(self.env.ref('sama_etat.government_project_view_tree').id, 'list'),
                      (self.env.ref('sama_etat.government_project_view_form').id, 'form'),
                      (self.env.ref('sama_etat.government_project_view_kanban').id, 'kanban')],
            'domain': [('status', 'in', ['validated', 'in_progress'])],
            'target': 'current',
        }
    
    def action_view_ministries(self):
        """Action pour voir tous les ministères"""
        return self.env.ref('sama_etat.government_ministry_action').read()[0]
    
    def action_view_budgets(self):
        """Action pour voir tous les budgets"""
        return self.env.ref('sama_etat.government_budget_action').read()[0]
    
    def action_view_upcoming_events(self):
        """Action pour voir les événements à venir"""
        today = fields.Date.today()
        future_date = today + timedelta(days=30)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Événements à Venir',
            'res_model': 'government.event',
            'view_mode': 'tree,form,calendar',
            'domain': [
                ('event_date', '>=', today),
                ('event_date', '<=', future_date),
                ('status', '=', 'planned')
            ],
            'target': 'current',
        }

    @api.model
    def action_open_dashboard_with_refresh(self):
        """
        Action to open the dashboard, ensuring computed fields are refreshed.
        This method will be called by the menu item.
        """
        # Get or create the singleton dashboard record
        dashboard = self.search([], limit=1)
        if not dashboard:
            dashboard = self.create({}) # Create if it doesn't exist

        # Force recomputation of all computed fields by writing to a dummy field
        # This is crucial for ensuring the dashboard data is fresh on load.
        dashboard.write({'last_update_date': fields.Datetime.now()})

        # Return the action to display the dashboard form view
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tableau de Bord',
            'res_model': 'senegal.plan.dashboard',
            'res_id': dashboard.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {'form_view_initial_mode': 'readonly', 'create': False, 'edit': False, 'delete': False},
        }
