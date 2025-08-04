from odoo import models, fields, api

class ProjectPublicInfoType(models.Model):
    _name = 'project.public.info.type'
    _description = 'Type d\'Information de Publication du Projet'
    _order = 'name'

    name = fields.Char(string='Nom du Type d\'Information', required=True)
    description = fields.Text(string='Description')
    code = fields.Char(string='Code')
    obligatoire = fields.Boolean(string='Publication Obligatoire', default=False)
    frequence_publication = fields.Selection([
        ('unique', 'Publication Unique'),
        ('mensuelle', 'Mensuelle'),
        ('trimestrielle', 'Trimestrielle'),
        ('semestrielle', 'Semestrielle'),
        ('annuelle', 'Annuelle'),
        ('sur_demande', 'Sur Demande')
    ], string='Fréquence de Publication', default='unique')
    
    # Relations inverses
    project_ids = fields.Many2many('project.public.project', 'project_info_type_rel', 'info_type_id', 'project_id', string='Projets')
    
    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Le nom du type d\'information doit être unique.'),
        ('unique_code', 'unique(code)', 'Le code du type d\'information doit être unique.')
    ]
