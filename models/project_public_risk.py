from odoo import models, fields, api

class ProjectPublicRisk(models.Model):
    _name = 'project.public.risk'
    _description = 'Risque du Projet Public'
    _order = 'probabilite desc, impact desc'

    project_id = fields.Many2one('project.public.project', string='Projet', required=True, ondelete='cascade')
    nom_risque = fields.Char(string='Nom du Risque', required=True)
    categorie_risque = fields.Selection([
        ('technique', 'Technique'),
        ('financier', 'Financier'),
        ('environnemental', 'Environnemental'),
        ('social', 'Social'),
        ('politique', 'Politique'),
        ('operationnel', 'Opérationnel'),
        ('juridique', 'Juridique'),
        ('autre', 'Autre')
    ], string='Catégorie de Risque', required=True)
    probabilite = fields.Selection([
        ('1', 'Très Faible (1)'),
        ('2', 'Faible (2)'),
        ('3', 'Moyenne (3)'),
        ('4', 'Élevée (4)'),
        ('5', 'Très Élevée (5)')
    ], string='Probabilité', required=True)
    impact = fields.Selection([
        ('1', 'Très Faible (1)'),
        ('2', 'Faible (2)'),
        ('3', 'Moyen (3)'),
        ('4', 'Élevé (4)'),
        ('5', 'Très Élevé (5)')
    ], string='Impact', required=True)
    niveau_risque = fields.Integer(string='Niveau de Risque', compute='_compute_niveau_risque', store=True)
    mesures_attenuation = fields.Text(string='Mesures d\'Atténuation', required=True)
    responsable_suivi = fields.Many2one('res.users', string='Responsable du Suivi')
    statut = fields.Selection([
        ('identifie', 'Identifié'),
        ('en_cours', 'En cours de traitement'),
        ('maitrise', 'Maîtrisé'),
        ('realise', 'Réalisé')
    ], string='Statut', default='identifie')
    
    @api.depends('probabilite', 'impact')
    def _compute_niveau_risque(self):
        for record in self:
            if record.probabilite and record.impact:
                record.niveau_risque = int(record.probabilite) * int(record.impact)
            else:
                record.niveau_risque = 0
    
    _sql_constraints = [
        ('unique_risk_project', 'unique(project_id, nom_risque)', 'Un risque ne peut être défini qu\'une seule fois par projet.')
    ]
