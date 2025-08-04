from odoo import models, fields, api

class ProjectPublicProcurement(models.Model):
    _name = 'project.public.procurement'
    _description = 'Marché Public du Projet'
    _order = 'date_lancement_prevue, nom_marche'

    project_id = fields.Many2one('project.public.project', string='Projet', required=True, ondelete='cascade')
    nom_marche = fields.Char(string='Nom du Marché', required=True)
    type_marche = fields.Selection([
        ('travaux', 'Travaux'),
        ('fournitures', 'Fournitures'),
        ('services', 'Services'),
        ('prestations_intellectuelles', 'Prestations Intellectuelles'),
        ('mixte', 'Mixte')
    ], string='Type de Marché', required=True)
    mode_passation = fields.Selection([
        ('appel_offres_ouvert', 'Appel d\'Offres Ouvert'),
        ('appel_offres_restreint', 'Appel d\'Offres Restreint'),
        ('demande_cotation', 'Demande de Cotation'),
        ('entente_directe', 'Entente Directe'),
        ('autre', 'Autre')
    ], string='Mode de Passation', required=True)
    montant_estime = fields.Monetary(string='Montant Estimé', currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id.id, required=True)
    date_lancement_prevue = fields.Date(string='Date Lancement Prévue')
    duree_execution_prevue = fields.Integer(string='Durée Exécution Prévue (jours)')
    description = fields.Text(string='Description')
    statut = fields.Selection([
        ('planifie', 'Planifié'),
        ('en_cours', 'En cours de passation'),
        ('attribue', 'Attribué'),
        ('execute', 'En cours d\'exécution'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé')
    ], string='Statut', default='planifie')
    
    _sql_constraints = [
        ('unique_marche_project', 'unique(project_id, nom_marche)', 'Un marché ne peut être défini qu\'une seule fois par projet.')
    ]
