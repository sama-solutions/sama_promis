from odoo import models, fields

class ProjectPublicRisk(models.Model):
    _name = 'project.public.risk'
    _description = 'Risque Projet Public'
    project_id = fields.Many2one('project.public.project', string='Projet', required=True, ondelete='cascade')
    nom_risque = fields.Char(string='Nom du Risque', required=True)
    description_risque = fields.Text(string='Description du Risque')
    categorie_risque = fields.Selection([
        ('technique', 'Technique'),
        ('financier', 'Financier'),
        ('environnemental', 'Environnemental'),
        ('social', 'Social'),
        ('politique', 'Politique'),
        ('operationnel', 'Opérationnel')
    ], string='Catégorie de Risque', required=True)
    probabilite = fields.Selection([
        ('faible', 'Faible'),
        ('moyenne', 'Moyenne'),
        ('elevee', 'Élevée')
    ], string='Probabilité', required=True)
    impact = fields.Selection([
        ('faible', 'Faible'),
        ('moyen', 'Moyen'),
        ('eleve', 'Élevé')
    ], string='Impact', required=True)
    mesures_attenuation = fields.Text(string='Mesures d\'Atténuation')
    responsable_suivi = fields.Char(string='Responsable du Suivi')

