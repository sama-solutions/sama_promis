from odoo import models, fields

class ProjectPublicPartner(models.Model):
    _name = 'project.public.partner'
    _description = 'Partenaire de Projet Public'
    project_id = fields.Many2one('project.public.project', string='Projet', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Partenaire', required=True)
    type_partenariat = fields.Char(string='Type de Partenariat', help="Ex: Financement, Assistance Technique, Co-exécution.")
    montant_contribution_estime = fields.Monetary(string='Montant Contribution Estimé', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id.id)

