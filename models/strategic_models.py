from odoo import models, fields, api

class StrategicPlan(models.Model):
    _name = 'strategic.plan'
    _description = 'Plan Sénégal 2050'

    name = fields.Char(string="Plan Sénégal 2050", default="Plan Sénégal 2050", required=True, readonly=True, states={'draft': [('readonly', False)]})
    vision = fields.Text(string="Description de la Vision", readonly=True, states={'draft': [('readonly', False)]})
    start_date = fields.Date(string="Date de Début", readonly=True, states={'draft': [('readonly', False)]})
    end_date = fields.Date(string="Date de Fin", readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('validated', 'Validé'),
        ('archived', 'Archivé')
    ], string="Statut", default='draft')
    pillar_ids = fields.One2many('strategic.pillar', 'plan_id', string="Piliers Stratégiques", readonly=True, states={'draft': [('readonly', False)]})

    def action_set_to_draft(self):
        self.write({'state': 'draft'})

class StrategicPillar(models.Model):
    _name = 'strategic.pillar'
    _description = 'Pilier Stratégique'

    name = fields.Char(string="Nom du Pilier", required=True, readonly=True, states={'draft': [('readonly', False)]})
    code = fields.Char(string="Code du Pilier", readonly=True, states={'draft': [('readonly', False)]})
    plan_id = fields.Many2one('strategic.plan', string="Plan Stratégique", required=True, readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Html(string="Description", readonly=True, states={'draft': [('readonly', False)]})
    axis_ids = fields.One2many('strategic.axis', 'pillar_id', string="Axes Stratégiques", readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Brouillon'), ('locked', 'Verrouillé')], string="État", default='locked', readonly=True, copy=False)

    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    def action_set_to_locked(self):
        self.write({'state': 'locked'})

class StrategicAxis(models.Model):
    _name = 'strategic.axis'
    _description = 'Axe Stratégique'

    name = fields.Char(string="Nom de l'Axe", required=True, readonly=True, states={'draft': [('readonly', False)]})
    code = fields.Char(string="Code de l'Axe", readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Text(string="Description", readonly=True, states={'draft': [('readonly', False)]})
    pillar_id = fields.Many2one('strategic.pillar', string="Pilier Stratégique", required=True, readonly=True, states={'draft': [('readonly', False)]})
    objective_ids = fields.One2many('strategic.objective', 'axis_id', string="Objectifs/Actions Prioritaires", readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Brouillon'), ('locked', 'Verrouillé')], string="État", default='locked', readonly=True, copy=False)

    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    def action_set_to_locked(self):
        self.write({'state': 'locked'})

class StrategicObjective(models.Model):
    _name = 'strategic.objective'
    _description = 'Objectif ou Action Prioritaire'

    name = fields.Char(string="Nom de l'Objectif", required=True, readonly=True, states={'draft': [('readonly', False)]})
    code = fields.Char(string="Code de l'Objectif", readonly=True, states={'draft': [('readonly', False)]})
    axis_id = fields.Many2one('strategic.axis', string="Axe Stratégique", required=True, readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Text(string="Description", readonly=True, states={'draft': [('readonly', False)]})
    kpi_ids = fields.One2many('strategic.kpi', 'objective_id', string="Indicateurs Clés de Performance", readonly=True, states={'draft': [('readonly', False)]}) # To be implemented later
    linked_projects = fields.One2many('government.project', 'strategic_objective_id', string="Projets Liés", readonly=True, states={'draft': [('readonly', False)]})
    linked_decisions = fields.One2many('government.decision', 'strategic_objective_id', string="Décisions Liées", readonly=True, states={'draft': [('readonly', False)]})
    linked_budgets = fields.One2many('government.budget', 'strategic_objective_id', string="Budgets Liés", readonly=True, states={'draft': [('readonly', False)]})
    linked_events = fields.One2many('government.event', 'strategic_objective_id', string="Événements Liés", readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Brouillon'), ('locked', 'Verrouillé')], string="État", default='locked', readonly=True, copy=False)

    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    def action_set_to_locked(self):
        self.write({'state': 'locked'})


class StrategicKpi(models.Model):
    _name = 'strategic.kpi'
    _description = 'Indicateur Clé de Performance'

    name = fields.Char(string="Nom de l'Indicateur", required=True, readonly=True, states={'draft': [('readonly', False)]})
    code = fields.Char(string="Code de l'Indicateur", readonly=True, states={'draft': [('readonly', False)]})
    objective_id = fields.Many2one('strategic.objective', string="Objectif Stratégique", required=True, readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Text(string="Description", readonly=True, states={'draft': [('readonly', False)]})
    target_value = fields.Float(string="Valeur Cible", readonly=True, states={'draft': [('readonly', False)]})
    current_value = fields.Float(string="Valeur Actuelle", readonly=True, states={'draft': [('readonly', False)]})
    unit_of_measure = fields.Char(string="Unité de Mesure", readonly=True, states={'draft': [('readonly', False)]})
    date_updated = fields.Date(string="Date de Mise à Jour", default=fields.Date.today, readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Brouillon'), ('locked', 'Verrouillé')], string="État", default='locked', readonly=True, copy=False)

    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    def action_set_to_locked(self):
        self.write({'state': 'locked'})