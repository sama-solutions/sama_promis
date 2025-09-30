# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date


class SamaPromisProcurementPlan(models.Model):
    """Plan de Passation de Marché - Procurement Plan Model"""
    
    _name = 'sama.promis.procurement.plan'
    _description = 'Plan de Passation de Marché'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'sama.promis.workflow.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'
    
    # Core Fields
    name = fields.Char(
        string='Titre',
        required=True,
        tracking=True,
        help="Titre du plan de passation de marché"
    )
    reference = fields.Char(
        string='Référence',
        readonly=True,
        copy=False,
        help="Référence unique générée automatiquement"
    )
    description = fields.Html(
        string='Description',
        help="Description détaillée du plan de passation"
    )
    project_id = fields.Many2one(
        'sama.promis.project',
        string='Projet',
        required=True,
        ondelete='cascade',
        tracking=True,
        help="Projet parent auquel ce plan est rattaché"
    )
    contract_id = fields.Many2one(
        'sama.promis.contract',
        string='Contrat',
        ondelete='set null',
        tracking=True,
        help="Contrat spécifique lié à ce plan (optionnel)"
    )
    fiscal_year = fields.Char(
        string='Année Fiscale',
        help="Année fiscale du plan (ex: 2024)"
    )
    plan_type = fields.Selection([
        ('annual', 'Annuel'),
        ('project_specific', 'Spécifique au Projet'),
        ('emergency', 'Urgence')
    ], string='Type de Plan', required=True, default='annual', tracking=True)
    
    # Financial Fields
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id,
        help="Devise pour tous les montants"
    )
    total_estimated_cost = fields.Monetary(
        string='Coût Estimé Total',
        compute='_compute_financial_totals',
        store=True,
        currency_field='currency_id',
        help="Somme des coûts estimés de toutes les lignes"
    )
    total_actual_cost = fields.Monetary(
        string='Coût Réel Total',
        compute='_compute_actual_costs',
        store=True,
        currency_field='currency_id',
        help="Somme des coûts réels de toutes les lignes"
    )
    budget_variance = fields.Monetary(
        string='Écart Budgétaire',
        compute='_compute_actual_costs',
        store=True,
        currency_field='currency_id',
        help="Différence entre coût estimé et coût réel"
    )
    budget_variance_percentage = fields.Float(
        string='Écart Budgétaire (%)',
        compute='_compute_budget_variance_percentage',
        store=True,
        help="Pourcentage d'écart budgétaire"
    )
    
    # Dates
    plan_start_date = fields.Date(
        string='Date Début Plan',
        required=True,
        tracking=True,
        help="Date de début des activités de passation"
    )
    plan_end_date = fields.Date(
        string='Date Fin Plan',
        required=True,
        tracking=True,
        help="Date de fin prévue pour toutes les passations"
    )
    approval_date = fields.Date(
        string='Date d\'Approbation',
        readonly=True,
        help="Date de validation du plan"
    )
    completion_date = fields.Date(
        string='Date de Finalisation',
        readonly=True,
        help="Date de finalisation du plan"
    )
    
    # State Management (override from WorkflowMixin)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('validated', 'Validé'),
        ('in_execution', 'En Exécution'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé')
    ], string='État', default='draft', required=True, tracking=True)
    
    # Relationships
    line_ids = fields.One2many(
        'sama.promis.procurement.plan.line',
        'plan_id',
        string='Lignes de Passation',
        help="Lignes de passation de marché"
    )
    responsible_id = fields.Many2one(
        'res.users',
        string='Responsable',
        default=lambda self: self.env.user,
        tracking=True,
        help="Personne responsable du plan"
    )
    
    # Computed Fields
    line_count = fields.Integer(
        string='Nombre de Lignes',
        compute='_compute_line_statistics',
        store=True
    )
    completed_line_count = fields.Integer(
        string='Lignes Terminées',
        compute='_compute_line_statistics',
        store=True
    )
    completion_rate = fields.Float(
        string='Taux de Complétion (%)',
        compute='_compute_line_statistics',
        store=True
    )
    is_overdue = fields.Boolean(
        string='En Retard',
        compute='_compute_overdue_status',
        help="Vrai si la date de fin est dépassée et l'état n'est pas terminé"
    )
    days_remaining = fields.Integer(
        string='Jours Restants',
        compute='_compute_days_remaining',
        help="Jours jusqu'à la date de fin"
    )
    
    # Constraints
    _sql_constraints = [
        ('check_dates', 'CHECK(plan_start_date <= plan_end_date)',
         'La date de début doit être antérieure ou égale à la date de fin.'),
        ('check_estimated_cost', 'CHECK(total_estimated_cost >= 0)',
         'Le coût estimé total doit être positif ou nul.')
    ]
    
    @api.model
    def create(self, vals):
        """Generate reference using sequence if not provided"""
        if not vals.get('reference'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('sama.promis.procurement.plan') or 'PROC-NEW'
        return super(SamaPromisProcurementPlan, self).create(vals)
    
    @api.depends('line_ids', 'line_ids.estimated_cost', 'line_ids.currency_id')
    def _compute_financial_totals(self):
        """Calculate total estimated cost by summing line amounts"""
        for plan in self:
            total = 0.0
            for line in plan.line_ids:
                if line.estimated_cost and line.currency_id:
                    # Convert to plan currency if different
                    if line.currency_id != plan.currency_id:
                        total += line.currency_id._convert(
                            line.estimated_cost,
                            plan.currency_id,
                            plan.env.company,
                            fields.Date.today()
                        )
                    else:
                        total += line.estimated_cost
            plan.total_estimated_cost = total
    
    @api.depends('line_ids', 'line_ids.actual_cost')
    def _compute_actual_costs(self):
        """Calculate total actual cost and budget variance"""
        for plan in self:
            total_actual = 0.0
            for line in plan.line_ids:
                if line.actual_cost:
                    if line.currency_id != plan.currency_id:
                        total_actual += line.currency_id._convert(
                            line.actual_cost,
                            plan.currency_id,
                            plan.env.company,
                            fields.Date.today()
                        )
                    else:
                        total_actual += line.actual_cost
            plan.total_actual_cost = total_actual
            plan.budget_variance = plan.total_actual_cost - plan.total_estimated_cost
    
    @api.depends('total_estimated_cost', 'total_actual_cost')
    def _compute_budget_variance_percentage(self):
        """Calculate percentage variance"""
        for plan in self:
            if plan.total_estimated_cost:
                plan.budget_variance_percentage = (plan.budget_variance / plan.total_estimated_cost) * 100
            else:
                plan.budget_variance_percentage = 0.0
    
    @api.depends('line_ids', 'line_ids.state')
    def _compute_line_statistics(self):
        """Calculate line count, completed count, and completion rate"""
        for plan in self:
            plan.line_count = len(plan.line_ids)
            plan.completed_line_count = len(plan.line_ids.filtered(lambda l: l.state == 'completed'))
            if plan.line_count:
                plan.completion_rate = (plan.completed_line_count / plan.line_count) * 100
            else:
                plan.completion_rate = 0.0
    
    @api.depends('plan_end_date', 'state')
    def _compute_overdue_status(self):
        """Determine if plan is overdue"""
        today = date.today()
        for plan in self:
            plan.is_overdue = (
                plan.plan_end_date and 
                plan.plan_end_date < today and 
                plan.state not in ('completed', 'cancelled')
            )
    
    @api.depends('plan_end_date')
    def _compute_days_remaining(self):
        """Calculate days until deadline"""
        today = date.today()
        for plan in self:
            if plan.plan_end_date:
                delta = plan.plan_end_date - today
                plan.days_remaining = delta.days
            else:
                plan.days_remaining = 0
    
    def _validate_state_transition(self, new_state):
        """Define allowed transitions"""
        allowed_transitions = {
            'draft': ['validated', 'cancelled'],
            'validated': ['in_execution', 'draft', 'cancelled'],
            'in_execution': ['completed', 'cancelled'],
            'completed': [],
            'cancelled': ['draft']
        }
        
        for record in self:
            if new_state not in allowed_transitions.get(record.state, []):
                raise ValidationError(
                    _("Transition invalide de '%s' vers '%s'.") % (
                        dict(self._fields['state'].selection).get(record.state),
                        dict(self._fields['state'].selection).get(new_state)
                    )
                )
        return True
    
    def _before_state_change(self, new_state):
        """Validate and set dates before state changes"""
        for record in self:
            if new_state == 'validated':
                if not record.line_ids:
                    raise ValidationError(_("Le plan doit contenir au moins une ligne avant validation."))
                record.approval_date = fields.Date.today()
            
            if new_state == 'completed':
                record.completion_date = fields.Date.today()
        
        return super(SamaPromisProcurementPlan, self)._before_state_change(new_state)
    
    def action_validate(self):
        """Change state to validated with validation checks"""
        self._validate_state_transition('validated')
        self._before_state_change('validated')
        self.write({'state': 'validated'})
        self._log_state_change('validated')
        return True
    
    def action_start_execution(self):
        """Change state to in_execution"""
        self._validate_state_transition('in_execution')
        self.write({'state': 'in_execution'})
        self._log_state_change('in_execution')
        return True
    
    def action_complete(self):
        """Change state to completed"""
        self._validate_state_transition('completed')
        self._before_state_change('completed')
        self.write({'state': 'completed'})
        self._log_state_change('completed')
        return True
    
    def action_cancel(self):
        """Change state to cancelled"""
        self._validate_state_transition('cancelled')
        self.write({'state': 'cancelled'})
        self._log_state_change('cancelled')
        return True
    
    def action_reset_to_draft(self):
        """Reset to draft (only from validated state)"""
        self._validate_state_transition('draft')
        self.write({
            'state': 'draft',
            'approval_date': False,
            'completion_date': False
        })
        self._log_state_change('draft')
        return True
    
    def action_view_lines(self):
        """Open tree view of procurement lines for this plan"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Lignes de Passation'),
            'res_model': 'sama.promis.procurement.plan.line',
            'view_mode': 'tree,form',
            'domain': [('plan_id', '=', self.id)],
            'context': {
                'default_plan_id': self.id,
            }
        }
    
    @api.constrains('project_id', 'contract_id')
    def _check_contract_project_consistency(self):
        """If contract_id is set, ensure it belongs to the same project_id"""
        for record in self:
            if record.contract_id and record.contract_id.project_id != record.project_id:
                raise ValidationError(
                    _("Le contrat sélectionné n'appartient pas au projet '%s'.") % record.project_id.name
                )
