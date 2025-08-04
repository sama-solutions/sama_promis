from odoo import models, fields, api

class ProjectPublicKPI(models.Model):
    _name = 'project.public.kpi'
    _description = 'Indicateur de Performance du Projet'
    _order = 'sequence'

    name = fields.Char('Indicateur', required=True)
    project_id = fields.Many2one('government.project', string='Projet', required=True)
    category = fields.Selection([
        ('output', 'Produit'),
        ('outcome', 'Résultat'),
        ('impact', 'Impact')
    ], string='Catégorie', required=True)
    baseline = fields.Float('Valeur de Base')
    target = fields.Float('Valeur Cible', required=True)
    current_value = fields.Float('Valeur Actuelle')
    unit = fields.Char('Unité de Mesure', required=True)
    frequency = fields.Selection([
        ('monthly', 'Mensuelle'),
        ('quarterly', 'Trimestrielle'),
        ('biannual', 'Semestrielle'),
        ('yearly', 'Annuelle')
    ], string='Fréquence de Collecte', required=True)
    sequence = fields.Integer('Séquence', default=10)
    notes = fields.Text('Notes Méthodologiques')
    
    progress = fields.Float('Progrès (%%)', compute='_compute_progress', store=True)
    
    @api.depends('target', 'current_value')
    def _compute_progress(self):
        for kpi in self:
            kpi.progress = (kpi.current_value / kpi.target * 100) if kpi.target else 0.0
