from odoo import models, fields

class ProjectPublicBudgetAnnual(models.Model):
    _name = 'project.public.budget.annual'
    _description = 'Répartition Annuelle du Budget Projet'
    project_id = fields.Many2one('project.public.project', string='Projet', required=True, ondelete='cascade')
    annee = fields.Integer(string='Année', required=True)
    montant_fcfa = fields.Monetary(string='Montant (FCFA)', currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id.id)

