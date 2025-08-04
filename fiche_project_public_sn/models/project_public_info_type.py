from odoo import models, fields

class ProjectPublicInfoType(models.Model):
    _name = 'project.public.info.type'
    _description = 'Type d\'Information de Publication'
    name = fields.Char(string='Nom du Type d\'Information', required=True)
    description = fields.Text(string='Description')

