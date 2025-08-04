from odoo import models, fields, api

class ProjectPublicPartner(models.Model):
    _name = 'project.public.partner'
    _description = 'Partenaire du Projet Public'
    _order = 'type_partenariat, partner_id'

    project_id = fields.Many2one('project.public.project', string='Projet', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Partenaire', required=True)
    type_partenariat = fields.Selection([
        ('technique', 'Partenaire Technique'),
        ('financier', 'Partenaire Financier'),
        ('technique_financier', 'Partenaire Technique et Financier'),
        ('execution', 'Partenaire d\'Exécution'),
        ('autre', 'Autre')
    ], string='Type de Partenariat', required=True)
    montant_contribution_estime = fields.Monetary(string='Montant Contribution Estimé', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id.id, required=True)
    role_description = fields.Text(string='Description du Rôle')
    contact_principal = fields.Char(string='Contact Principal')
    
    _sql_constraints = [
        ('unique_partner_project', 'unique(project_id, partner_id)', 'Un partenaire ne peut être associé qu\'une seule fois à un projet.')
    ]
