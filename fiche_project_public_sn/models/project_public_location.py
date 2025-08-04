from odoo import models, fields

class ProjectPublicLocationDepartement(models.Model):
    _name = 'project.public.location.departement'
    _description = 'Département'
    name = fields.Char(string='Nom du Département', required=True)
    state_id = fields.Many2one('res.country.state', string='Région', domain=[('country_id.code', '=', 'SN')], required=True)

class ProjectPublicLocationCommune(models.Model):
    _name = 'project.public.location.commune'
    _description = 'Commune'
    name = fields.Char(string='Nom de la Commune', required=True)
    departement_id = fields.Many2one('project.public.location.departement', string='Département', required=True)

