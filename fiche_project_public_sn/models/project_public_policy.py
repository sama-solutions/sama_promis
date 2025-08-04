from odoo import models, fields

class ProjectPublicPolicy(models.Model):
    _name = 'project.public.policy'
    _description = 'Politique Publique de Référence'
    name = fields.Char(string='Nom de la Politique Publique', required=True)
    code = fields.Char(string='Code/Référence')
    description = fields.Text(string='Description')

