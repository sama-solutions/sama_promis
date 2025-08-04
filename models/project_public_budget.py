from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProjectPublicBudgetAnnual(models.Model):
    _name = 'project.public.budget.annual'
    _description = 'Répartition Budgétaire Annuelle du Projet'
    _order = 'year'

    project_id = fields.Many2one('project.public.project', string='Projet', required=True, ondelete='cascade')
    annee = fields.Integer(string='Année', required=True)
    year = fields.Integer(string='Année', required=True)  # Keep both for compatibility
    montant_fcfa = fields.Monetary(string='Montant FCFA', currency_field='currency_id', required=True)
    planned_amount = fields.Monetary(string='Montant Planifié', currency_field='currency_id', required=True)
    allocated_amount = fields.Monetary(string='Montant Alloué', currency_field='currency_id')
    spent_amount = fields.Monetary(string='Montant Dépensé', currency_field='currency_id')
    remaining_amount = fields.Monetary(string='Montant Restant', currency_field='currency_id', compute='_compute_remaining_amount', store=True)
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id.id, required=True)
    
    notes = fields.Text(string='Notes')
    
    @api.depends('allocated_amount', 'spent_amount')
    def _compute_remaining_amount(self):
        for record in self:
            record.remaining_amount = record.allocated_amount - record.spent_amount
    
    @api.constrains('year')
    def _check_year(self):
        for record in self:
            if record.year < 2020 or record.year > 2060:
                raise ValidationError("L'année doit être comprise entre 2020 et 2060.")
    
    _sql_constraints = [
        ('unique_project_year', 'unique(project_id, year)', 'Il ne peut y avoir qu\'une seule répartition budgétaire par année pour un projet donné.')
    ]
