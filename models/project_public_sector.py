from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProjectPublicSector(models.Model):
    _name = 'project.public.sector'
    _description = 'Secteur d\'Intervention du Projet Public'
    _order = 'name'

    name = fields.Char(string='Nom du Secteur', required=True)
    code = fields.Char(string='Code du Secteur')
    description = fields.Text(string='Description')
    parent_id = fields.Many2one('project.public.sector', string='Secteur Parent')
    child_ids = fields.One2many('project.public.sector', 'parent_id', string='Sous-secteurs')
    
    # Relations inverses
    project_ids = fields.One2many('project.public.project', 'secteur_intervention', string='Projets')
    
    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Le nom du secteur doit être unique.'),
        ('unique_code', 'unique(code)', 'Le code du secteur doit être unique.')
    ]
    
    @api.constrains('parent_id')
    def _check_parent_recursion(self):
        if not self._check_recursion():
            raise ValidationError("Vous ne pouvez pas créer de secteurs récursifs.")
