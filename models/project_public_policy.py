from odoo import models, fields, api

class ProjectPublicPolicy(models.Model):
    _name = 'project.public.policy'
    _description = 'Politique Publique de Référence'
    _order = 'name'

    name = fields.Char(string='Nom de la Politique', required=True)
    code = fields.Char(string='Code de la Politique')
    description = fields.Text(string='Description')
    type_politique = fields.Selection([
        ('nationale', 'Politique Nationale'),
        ('sectorielle', 'Politique Sectorielle'),
        ('regionale', 'Politique Régionale'),
        ('locale', 'Politique Locale'),
        ('internationale', 'Engagement International')
    ], string='Type de Politique', default='nationale')
    date_adoption = fields.Date(string='Date d\'Adoption')
    date_expiration = fields.Date(string='Date d\'Expiration')
    statut = fields.Selection([
        ('active', 'Active'),
        ('en_cours', 'En cours d\'élaboration'),
        ('suspendue', 'Suspendue'),
        ('expiree', 'Expirée')
    ], string='Statut', default='active')
    
    # Relations inverses
    project_ids = fields.Many2many('project.public.project', 'project_policy_rel', 'policy_id', 'project_id', string='Projets Liés')
    
    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Le nom de la politique doit être unique.'),
        ('unique_code', 'unique(code)', 'Le code de la politique doit être unique.')
    ]
