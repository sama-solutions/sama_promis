# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date


class SamaPromisProcurementPlanLine(models.Model):
    """Ligne de Plan de Passation de Marché - Procurement Plan Line Model"""
    
    _name = 'sama.promis.procurement.plan.line'
    _description = 'Ligne de Plan de Passation de Marché'
    _inherit = ['mail.thread']
    _order = 'sequence, planned_date, id'
    _rec_name = 'description'
    
    # Core Fields
    sequence = fields.Integer(
        string='Séquence',
        default=10,
        help="Pour l'ordre manuel dans la vue arbre"
    )
    plan_id = fields.Many2one(
        'sama.promis.procurement.plan',
        string='Plan de Passation',
        required=True,
        ondelete='cascade',
        help="Plan parent"
    )
    description = fields.Char(
        string='Description',
        required=True,
        tracking=True,
        help="Description courte de l'élément de passation"
    )
    detailed_description = fields.Text(
        string='Description Détaillée',
        help="Spécifications détaillées"
    )
    reference = fields.Char(
        string='Référence',
        help="Numéro de référence externe si applicable"
    )
    
    # Procurement Details
    procurement_method = fields.Selection([
        ('open_tender', 'Appel d\'Offres Ouvert'),
        ('restricted_tender', 'Appel d\'Offres Restreint'),
        ('competitive_quotation', 'Demande de Cotation'),
        ('direct_contracting', 'Gré à Gré'),
        ('framework_agreement', 'Accord-Cadre'),
        ('shopping', 'Shopping'),
        ('other', 'Autre')
    ], string='Méthode de Passation', required=True, tracking=True)
    
    procurement_category = fields.Selection([
        ('goods', 'Biens'),
        ('works', 'Travaux'),
        ('services', 'Services Consulting'),
        ('non_consulting_services', 'Services Non-Consulting')
    ], string='Catégorie', required=True, tracking=True)
    
    threshold_type = fields.Selection([
        ('below_threshold', 'Sous Seuil'),
        ('above_threshold', 'Au-dessus du Seuil'),
        ('prior_review', 'Revue Préalable'),
        ('post_review', 'Revue A Posteriori')
    ], string='Type de Seuil', help="Pour la conformité aux bailleurs")
    
    # Financial Fields
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        related='plan_id.currency_id',
        store=True,
        help="Héritée du plan"
    )
    estimated_cost = fields.Monetary(
        string='Coût Estimé',
        required=True,
        currency_field='currency_id',
        tracking=True,
        help="Montant budgété/estimé"
    )
    actual_cost = fields.Monetary(
        string='Coût Réel',
        currency_field='currency_id',
        tracking=True,
        help="Montant contracté/dépensé réel"
    )
    cost_variance = fields.Monetary(
        string='Écart de Coût',
        compute='_compute_cost_variance',
        store=True,
        currency_field='currency_id',
        help="Différence entre coût estimé et coût réel"
    )
    cost_variance_percentage = fields.Float(
        string='Écart de Coût (%)',
        compute='_compute_cost_variance',
        store=True,
        help="Pourcentage d'écart de coût"
    )
    
    # Timeline
    planned_date = fields.Date(
        string='Date Prévue Lancement',
        required=True,
        tracking=True,
        help="Date prévue de lancement de la passation"
    )
    planned_completion_date = fields.Date(
        string='Date Prévue Finalisation',
        tracking=True,
        help="Date prévue de signature du contrat"
    )
    actual_start_date = fields.Date(
        string='Date Réelle Début',
        readonly=True,
        help="Date réelle de début de la passation"
    )
    actual_completion_date = fields.Date(
        string='Date Réelle Finalisation',
        readonly=True,
        help="Date réelle de signature du contrat"
    )
    delay_days = fields.Integer(
        string='Jours de Retard',
        compute='_compute_delay',
        help="Jours de retard si applicable"
    )
    
    # Status Tracking
    state = fields.Selection([
        ('planned', 'Planifié'),
        ('in_progress', 'En Cours'),
        ('awarded', 'Attribué'),
        ('contracted', 'Contracté'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé')
    ], string='État', default='planned', tracking=True)
    
    progress_notes = fields.Text(
        string='Notes de Progression',
        help="Notes sur l'avancement de la passation"
    )
    contract_reference = fields.Char(
        string='Référence Contrat',
        help="Référence du contrat attribué si applicable"
    )
    supplier_id = fields.Many2one(
        'res.partner',
        string='Fournisseur/Contractant',
        help="Fournisseur ou contractant sélectionné"
    )
    
    # Compliance Fields (basic - Phase 3 will expand)
    requires_prior_review = fields.Boolean(
        string='Revue Préalable Requise',
        default=False,
        help="Nécessite une revue préalable du bailleur"
    )
    review_status = fields.Selection([
        ('not_required', 'Non Requis'),
        ('pending', 'En Attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté')
    ], string='Statut de Revue', default='not_required')
    
    donor_approval_date = fields.Date(
        string='Date Approbation Bailleur',
        help="Date d'approbation par le bailleur (si applicable)"
    )
    
    # Computed Fields
    is_delayed = fields.Boolean(
        string='En Retard',
        compute='_compute_delay',
        help="Vrai si les dates réelles dépassent les dates prévues"
    )
    project_id = fields.Many2one(
        'sama.promis.project',
        string='Projet',
        related='plan_id.project_id',
        store=True,
        help="Pour faciliter le filtrage"
    )
    
    # Constraints
    _sql_constraints = [
        ('check_estimated_cost_positive', 'CHECK(estimated_cost > 0)',
         'Le coût estimé doit être strictement positif.'),
        ('check_dates', 'CHECK(planned_date <= planned_completion_date OR planned_completion_date IS NULL)',
         'La date prévue de lancement doit être antérieure ou égale à la date prévue de finalisation.')
    ]
    
    @api.constrains('actual_start_date', 'actual_completion_date')
    def _check_actual_dates(self):
        """Ensure actual_start_date <= actual_completion_date if both set"""
        for record in self:
            if record.actual_start_date and record.actual_completion_date:
                if record.actual_start_date > record.actual_completion_date:
                    raise ValidationError(
                        _("La date réelle de début doit être antérieure ou égale à la date réelle de finalisation.")
                    )
    
    @api.depends('estimated_cost', 'actual_cost')
    def _compute_cost_variance(self):
        """Calculate cost variance and percentage"""
        for line in self:
            if line.actual_cost:
                line.cost_variance = line.actual_cost - line.estimated_cost
                if line.estimated_cost:
                    line.cost_variance_percentage = (line.cost_variance / line.estimated_cost) * 100
                else:
                    line.cost_variance_percentage = 0.0
            else:
                line.cost_variance = 0.0
                line.cost_variance_percentage = 0.0
    
    @api.depends('planned_completion_date', 'actual_completion_date')
    def _compute_delay(self):
        """Calculate delay days and is_delayed"""
        for line in self:
            if line.planned_completion_date and line.actual_completion_date:
                delta = line.actual_completion_date - line.planned_completion_date
                line.delay_days = delta.days if delta.days > 0 else 0
                line.is_delayed = delta.days > 0
            elif line.planned_completion_date and not line.actual_completion_date and line.state in ('in_progress', 'awarded'):
                # Check if we're past the planned completion date
                today = date.today()
                if today > line.planned_completion_date:
                    delta = today - line.planned_completion_date
                    line.delay_days = delta.days
                    line.is_delayed = True
                else:
                    line.delay_days = 0
                    line.is_delayed = False
            else:
                line.delay_days = 0
                line.is_delayed = False
    
    @api.onchange('procurement_method')
    def _onchange_procurement_method(self):
        """Suggest threshold_type based on method"""
        if self.procurement_method in ('open_tender', 'restricted_tender'):
            self.threshold_type = 'above_threshold'
        elif self.procurement_method in ('competitive_quotation', 'shopping', 'direct_contracting'):
            self.threshold_type = 'below_threshold'
    
    def action_start_procurement(self):
        """Set state to in_progress, set actual_start_date to today"""
        for record in self:
            record.write({
                'state': 'in_progress',
                'actual_start_date': fields.Date.today()
            })
        return True
    
    def action_award(self):
        """Set state to awarded"""
        for record in self:
            record.write({'state': 'awarded'})
        return True
    
    def action_contract(self):
        """Set state to contracted, set actual_completion_date"""
        for record in self:
            record.write({
                'state': 'contracted',
                'actual_completion_date': fields.Date.today()
            })
        return True
    
    def action_complete(self):
        """Set state to completed"""
        for record in self:
            record.write({'state': 'completed'})
        return True
    
    def action_cancel(self):
        """Set state to cancelled"""
        for record in self:
            record.write({'state': 'cancelled'})
        return True
    
    def action_reset_to_planned(self):
        """Reset to planned state (only from in_progress)"""
        for record in self:
            if record.state == 'in_progress':
                record.write({
                    'state': 'planned',
                    'actual_start_date': False
                })
        return True
    
    @api.constrains('plan_id', 'planned_date')
    def _check_date_within_plan(self):
        """Ensure planned_date is within plan's date range"""
        for record in self:
            if record.plan_id and record.planned_date:
                if record.planned_date < record.plan_id.plan_start_date or record.planned_date > record.plan_id.plan_end_date:
                    raise ValidationError(
                        _("La date prévue de lancement doit être comprise entre %s et %s (dates du plan).") % (
                            record.plan_id.plan_start_date,
                            record.plan_id.plan_end_date
                        )
                    )
