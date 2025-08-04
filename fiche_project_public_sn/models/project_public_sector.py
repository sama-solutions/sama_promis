from odoo import models, fields

class ProjectPublicSector(models.Model):
    _name = 'project.public.sector'
    _description = 'Secteur d\'Intervention des Projets Publics'
    name = fields.Char(string='Nom du Secteur', required=True)
    code = fields.Char(string='Code du Secteur')

