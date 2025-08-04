from odoo import models, fields, api

class ProjectPublicIndicator(models.Model):
    _name = 'project.public.indicator'
    _description = 'Indicateur de Performance du Projet'
    _order = 'type_indicateur, nom_indicateur'

    project_id = fields.Many2one('project.public.project', string='Projet', required=True, ondelete='cascade')
    nom_indicateur = fields.Char(string='Nom de l\'Indicateur', required=True)
    type_indicateur = fields.Selection([
        ('quantitatif', 'Quantitatif'),
        ('qualitatif', 'Qualitatif'),
        ('impact', 'Impact'),
        ('resultat', 'Résultat'),
        ('processus', 'Processus')
    ], string='Type d\'Indicateur', required=True)
    unite_mesure = fields.Char(string='Unité de Mesure')
    valeur_baseline = fields.Float(string='Valeur de Base')
    valeur_cible = fields.Float(string='Valeur Cible')
    valeur_actuelle = fields.Float(string='Valeur Actuelle')
    frequence_mesure = fields.Selection([
        ('mensuelle', 'Mensuelle'),
        ('trimestrielle', 'Trimestrielle'),
        ('semestrielle', 'Semestrielle'),
        ('annuelle', 'Annuelle'),
        ('ponctuelle', 'Ponctuelle')
    ], string='Fréquence de Mesure', default='trimestrielle')
    source_donnees = fields.Char(string='Source des Données')
    responsable_collecte = fields.Many2one('res.users', string='Responsable de la Collecte')
    description = fields.Text(string='Description')
    
    _sql_constraints = [
        ('unique_indicator_project', 'unique(project_id, nom_indicateur)', 'Un indicateur ne peut être défini qu\'une seule fois par projet.')
    ]
