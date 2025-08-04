from odoo import models, fields

class ProjectPublicIndicator(models.Model):
    _name = 'project.public.indicator'
    _description = 'Indicateur de Performance Projet'
    project_id = fields.Many2one('project.public.project', string='Projet', required=True, ondelete='cascade')
    nom_indicateur = fields.Char(string='Nom de l\'Indicateur', required=True)
    type_indicateur = fields.Selection([
        ('quantitatif', 'Quantitatif'),
        ('qualitatif', 'Qualitatif')
    ], string='Type d\'Indicateur', required=True)
    unite_mesure = fields.Char(string='Unité de Mesure', help="Ex: Nombre, %, Km, etc.")
    valeur_cible = fields.Float(string='Valeur Cible')
    valeur_baseline = fields.Float(string='Valeur de Référence (Baseline)')
    frequence_mesure = fields.Selection([
        ('mensuel', 'Mensuel'),
        ('trimestriel', 'Trimestriel'),
        ('semestriel', 'Semestriel'),
        ('annuel', 'Annuel')
    ], string='Fréquence de Mesure', default='trimestriel')
    source_donnees = fields.Char(string='Source des Données')
    responsable_collecte = fields.Char(string='Responsable de la Collecte')

