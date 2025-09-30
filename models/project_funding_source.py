# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SamaPromisProjectFundingSource(models.Model):
    """Model to manage multiple funding sources per project."""
    
    _name = 'sama.promis.project.funding.source'
    _description = 'Source de Financement de Projet'
    _inherit = ['mail.thread']
    _order = 'sequence, id'
    
    # Basic Information
    name = fields.Char(
        string='Nom',
        required=True,
        tracking=True,
        help="Label pour cette source de financement (ex: 'Contribution BM 2024')"
    )
    
    project_id = fields.Many2one(
        'sama.promis.project',
        string='Projet',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Bailleur',
        required=True,
        domain=[('is_donor', '=', True)],
        tracking=True,
        help="Le bailleur de fonds pour cette source"
    )
    
    # Financial Information
    amount = fields.Monetary(
        string='Montant',
        required=True,
        currency_field='currency_id',
        tracking=True,
        help="Montant du financement"
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        required=True,
        default=lambda self: self.env.company.currency_id,
        tracking=True
    )
    
    funding_type = fields.Selection([
        ('grant', 'Subvention'),
        ('loan', 'Prêt'),
        ('co_financing', 'Cofinancement'),
        ('in_kind', 'En nature'),
        ('other', 'Autre')
    ], string='Type de Financement', required=True, default='grant', tracking=True)
    
    # Origin Classification
    funding_origin = fields.Selection([
        ('international', 'International'),
        ('local', 'Local')
    ], string='Origine', compute='_compute_funding_origin', store=True, tracking=True,
       help="Origine du financement (calculée automatiquement basée sur le pays du bailleur)")
    
    funding_origin_manual = fields.Selection([
        ('international', 'International'),
        ('local', 'Local')
    ], string='Origine Manuelle', tracking=True,
       help="Définir manuellement l'origine du financement (remplace le calcul automatique)")
    
    percentage_of_total = fields.Float(
        string='Pourcentage du Total',
        compute='_compute_percentage',
        store=True,
        help="Pourcentage de cette source par rapport au budget total du projet"
    )
    
    # Additional Information
    description = fields.Text(string='Description', help="Notes additionnelles sur cette source de financement")
    
    sequence = fields.Integer(string='Séquence', default=10, help="Ordre d'affichage")
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('received', 'Reçu'),
        ('cancelled', 'Annulé')
    ], string='État', default='draft', tracking=True)
    
    # Dates
    commitment_date = fields.Date(
        string='Date d\'Engagement',
        tracking=True,
        help="Date à laquelle le financement a été engagé"
    )
    
    received_date = fields.Date(
        string='Date de Réception',
        tracking=True,
        help="Date à laquelle le financement a été effectivement reçu"
    )
    
    contract_reference = fields.Char(
        string='Référence Contrat',
        tracking=True,
        help="Référence de l'accord de financement ou du contrat"
    )
    
    # SQL Constraints
    _sql_constraints = [
        ('check_amount_positive', 'CHECK(amount > 0)', 
         'Le montant du financement doit être positif!')
    ]
    
    @api.depends('partner_id', 'partner_id.country_id', 'funding_origin_manual')
    def _compute_funding_origin(self):
        """Compute funding origin based on partner's country vs company country."""
        company_country = self.env.company.country_id
        
        for source in self:
            # Use manual override if set
            if source.funding_origin_manual:
                source.funding_origin = source.funding_origin_manual
            elif source.partner_id and source.partner_id.country_id:
                # Compare partner country with company country
                if source.partner_id.country_id != company_country:
                    source.funding_origin = 'international'
                else:
                    source.funding_origin = 'local'
            else:
                # Default to local if no country specified
                source.funding_origin = 'local'
    
    @api.depends('amount', 'project_id.total_budget_computed')
    def _compute_percentage(self):
        """Calculate percentage of total project budget."""
        for source in self:
            if source.project_id and source.project_id.total_budget_computed > 0:
                source.percentage_of_total = (source.amount / source.project_id.total_budget_computed) * 100
            else:
                source.percentage_of_total = 0.0
    
    @api.constrains('currency_id', 'project_id')
    def _check_currency_consistency(self):
        """Warn if currency differs from project currency (but allow it)."""
        for source in self:
            if source.project_id and source.currency_id != source.project_id.currency_id:
                # Just log a warning, don't block
                self.env['ir.logging'].sudo().create({
                    'name': 'sama.promis.project.funding.source',
                    'type': 'server',
                    'level': 'warning',
                    'message': f"Source de financement {source.name} utilise une devise différente du projet",
                    'path': 'models/project_funding_source',
                    'func': '_check_currency_consistency',
                })
    
    def action_confirm(self):
        """Confirm the funding source."""
        self.write({'state': 'confirmed'})
        return True
    
    def action_mark_received(self):
        """Mark funding as received."""
        self.write({
            'state': 'received',
            'received_date': fields.Date.today()
        })
        return True
    
    def action_cancel(self):
        """Cancel the funding source."""
        self.write({'state': 'cancelled'})
        return True
    
    @api.model
    def create(self, vals):
        """Override create to trigger project budget recalculation."""
        result = super(SamaPromisProjectFundingSource, self).create(vals)
        if result.project_id:
            result.project_id._compute_funding_totals()
        return result
    
    def write(self, vals):
        """Override write to trigger project budget recalculation."""
        result = super(SamaPromisProjectFundingSource, self).write(vals)
        # Recalculate project totals if amount or currency changed
        if 'amount' in vals or 'currency_id' in vals or 'funding_origin' in vals:
            for source in self:
                if source.project_id:
                    source.project_id._compute_funding_totals()
        return result
    
    def unlink(self):
        """Override unlink to trigger project budget recalculation."""
        projects = self.mapped('project_id')
        result = super(SamaPromisProjectFundingSource, self).unlink()
        for project in projects:
            project._compute_funding_totals()
        return result
