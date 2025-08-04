from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProjectPublicLocationDepartement(models.Model):
    _name = 'project.public.location.departement'
    _description = 'Département - Localisation Projet Public'
    _order = 'name'

    name = fields.Char(string='Nom du Département', required=True)
    code = fields.Char(string='Code Département')
    region_id = fields.Many2one('res.country.state', string='Région', domain=[('country_id.code', '=', 'SN')])
    description = fields.Text(string='Description')
    
    # Relations inverses
    project_ids = fields.Many2many('project.public.project', 'project_departement_rel', 'departement_id', 'project_id', string='Projets')
    commune_ids = fields.One2many('project.public.location.commune', 'departement_id', string='Communes')
    
    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Le nom du département doit être unique.')
    ]

class ProjectPublicLocationCommune(models.Model):
    _name = 'project.public.location.commune'
    _description = 'Commune - Localisation Projet Public'
    _order = 'name'

    name = fields.Char(string='Nom de la Commune', required=True)
    code = fields.Char(string='Code Commune')
    departement_id = fields.Many2one('project.public.location.departement', string='Département')
    type_commune = fields.Selection([
        ('urbaine', 'Commune Urbaine'),
        ('rurale', 'Commune Rurale')
    ], string='Type de Commune', default='rurale')
    population = fields.Integer(string='Population Estimée')
    description = fields.Text(string='Description')
    
    # Coordonnées GPS
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
    
    # Relations inverses
    project_ids = fields.Many2many('project.public.project', 'project_commune_rel', 'commune_id', 'project_id', string='Projets')
    
    _sql_constraints = [
        ('unique_name_departement', 'unique(name, departement_id)', 'Le nom de la commune doit être unique par département.')
    ]
    
    @api.constrains('latitude', 'longitude')
    def _check_coordinates(self):
        for record in self:
            if record.latitude and (record.latitude < -90 or record.latitude > 90):
                raise ValidationError("La latitude doit être comprise entre -90 et 90 degrés.")
            if record.longitude and (record.longitude < -180 or record.longitude > 180):
                raise ValidationError("La longitude doit être comprise entre -180 et 180 degrés.")
